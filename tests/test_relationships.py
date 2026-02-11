"""TDD tests for relationship query tool.

Tests written first per Phase 0 plan S0.2.
"""

from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from relationship_query import (
    VocabularyError,
    add,
    load,
    parse_position,
    query,
    render_matrix,
    validate_relationships,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def sample_rels() -> dict:
    """Load the sample relationships fixture."""
    return load(FIXTURES / "sample_relationships.yaml")


# ---------------------------------------------------------------------------
# Core query/mutation
# ---------------------------------------------------------------------------


def test_query_by_entity_returns_all_aliases(sample_rels):
    """Querying 'marcus' should return results including alias-resolved matches."""
    results = query(sample_rels, entity="marcus")
    assert len(results) >= 3
    assert any(r["from"] == "marcus" for r in results)


def test_query_by_alias_string(sample_rels):
    """Querying by alias 'the soldier' should resolve to marcus's relationships."""
    results = query(sample_rels, entity="the soldier")
    assert len(results) >= 1
    assert any(r["from"] == "marcus" or r["to"] == "marcus" for r in results)


def test_add_rejects_unknown_rel_vocabulary(sample_rels):
    """Cannot add a relationship with rel='is_suspicious_of' (not in vocab)."""
    with pytest.raises(VocabularyError):
        add(
            sample_rels,
            from_e="marcus",
            to_e="elena",
            rel="is_suspicious_of",
            context="test",
            valid_from="Act1/Ch1",
            confidence="medium",
            source="canon/acts/act-1/ch1-outline.md#L1",
        )


def test_add_valid_relationship(sample_rels):
    """Adding a valid relationship appends and preserves existing."""
    before_count = len(sample_rels["relationships"])
    new_rel = add(
        sample_rels,
        from_e="marcus",
        to_e="zone_3",
        rel="fears",
        context="first encounter",
        valid_from="Act1/Ch2",
        confidence="medium",
        source="canon/acts/act-1/ch2-outline.md#L5",
    )
    assert len(sample_rels["relationships"]) == before_count + 1
    assert new_rel["id"].startswith("rel_")
    assert new_rel["rel"] == "fears"


def test_add_generates_sequential_ids(sample_rels):
    """Each add should produce incrementing IDs."""
    r1 = add(
        sample_rels, "marcus", "elena", "knows", "test1",
        "Act1/Ch1", "low", "canon/file.md",
    )
    r2 = add(
        sample_rels, "elena", "marcus", "knows", "test2",
        "Act1/Ch1", "low", "canon/file.md",
    )
    # Extract numeric parts
    n1 = int(r1["id"].split("_")[1])
    n2 = int(r2["id"].split("_")[1])
    assert n2 == n1 + 1


def test_render_matrix_produces_markdown(sample_rels):
    """render_matrix should output a valid markdown table."""
    md = render_matrix(sample_rels, as_of="Act1/Ch5")
    assert "| From" in md
    assert "marcus" in md.lower()


def test_render_matrix_empty_entities():
    """render_matrix with no entities should return a message."""
    data = {"rel_vocabulary": {}, "entities": {}, "relationships": []}
    md = render_matrix(data)
    assert "no entities" in md.lower()


# ---------------------------------------------------------------------------
# Temporal ordering
# ---------------------------------------------------------------------------


def test_query_as_of_filters_temporally(sample_rels):
    """Querying as_of='Act1/Ch3' should not return relationships from Act2."""
    results = query(sample_rels, entity="marcus", as_of="Act1/Ch3")
    for r in results:
        assert parse_position(r["valid_from"]) <= parse_position("Act1/Ch3")


def test_query_as_of_handles_double_digit_chapters(sample_rels):
    """Act1/Ch10 must sort after Act1/Ch9, not before."""
    results = query(sample_rels, entity="marcus", as_of="Act1/Ch10")
    for r in results:
        assert parse_position(r["valid_from"]) <= (1, 10)


def test_parse_position_act_ch():
    """Standard Act/Ch format should parse correctly."""
    assert parse_position("Act1/Ch3") == (1, 3)
    assert parse_position("Act2/Ch12") == (2, 12)
    assert parse_position("Act10/Ch1") == (10, 1)


def test_parse_position_l_format():
    """L{N}/{word} format should return (0, 0)."""
    assert parse_position("L1/concept") == (0, 0)
    assert parse_position("L2/arc") == (0, 0)


def test_parse_position_invalid_raises():
    """Invalid format should raise ValueError."""
    with pytest.raises(ValueError):
        parse_position("chapter-3")
    with pytest.raises(ValueError):
        parse_position("act1ch3")


def test_query_as_of_excludes_expired(sample_rels):
    """Relationships with valid_to before as_of should be excluded."""
    # rel_005 has valid_to: Act1/Ch9, so querying at Act1/Ch10 should exclude it
    results = query(sample_rels, entity="marcus", as_of="Act1/Ch10")
    ids = [r["id"] for r in results]
    assert "rel_005" not in ids


def test_query_as_of_includes_not_yet_expired(sample_rels):
    """Relationships with valid_to after as_of should be included."""
    # rel_005 has valid_to: Act1/Ch9, querying at Act1/Ch5 should include it
    results = query(sample_rels, entity="marcus", as_of="Act1/Ch5")
    ids = [r["id"] for r in results]
    assert "rel_005" in ids


# ---------------------------------------------------------------------------
# Semantic integrity edge cases
# ---------------------------------------------------------------------------


def test_validate_catches_broken_supersession():
    """If rel_002 says supersedes: rel_001, but rel_001 has no superseded_by."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {},
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "trusts",
                "context": "x", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "canon/file.md", "supersedes": None, "superseded_by": None,
            },
            {
                "id": "rel_002", "from": "a", "to": "b", "rel": "trusts",
                "context": "y", "valid_from": "Act2/Ch1", "confidence": "high",
                "source": "canon/file.md", "supersedes": "rel_001", "superseded_by": None,
            },
        ],
    }
    result = validate_relationships(data)
    assert not result.ok
    assert any("supersession" in e.lower() or "supersedes" in e.lower() for e in result.errors)


def test_validate_catches_circular_supersession():
    """rel_001 supersedes rel_002 supersedes rel_001 should fail."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {},
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "trusts",
                "context": "x", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "canon/file.md",
                "supersedes": "rel_002", "superseded_by": "rel_002",
            },
            {
                "id": "rel_002", "from": "a", "to": "b", "rel": "trusts",
                "context": "y", "valid_from": "Act2/Ch1", "confidence": "high",
                "source": "canon/file.md",
                "supersedes": "rel_001", "superseded_by": "rel_001",
            },
        ],
    }
    result = validate_relationships(data)
    assert not result.ok
    assert any("circular" in e.lower() for e in result.errors)


def test_validate_catches_duplicate_relationship_ids():
    """Two relationships with the same ID should fail validation."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {},
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "trusts",
                "context": "x", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "canon/file.md",
            },
            {
                "id": "rel_001", "from": "c", "to": "d", "rel": "trusts",
                "context": "y", "valid_from": "Act1/Ch2", "confidence": "high",
                "source": "canon/file.md",
            },
        ],
    }
    result = validate_relationships(data)
    assert not result.ok
    assert any("duplicate" in e.lower() for e in result.errors)


def test_validate_catches_alias_collision():
    """Two different entities claiming the same alias should fail."""
    data = {
        "rel_vocabulary": {"positive": [], "negative": [], "neutral": [], "causal": []},
        "entities": {
            "marcus": {
                "type": "character",
                "aliases": ["Marcus", "the soldier"],
                "introduced": "L1/concept",
            },
            "jonas": {
                "type": "character",
                "aliases": ["Jonas", "the soldier"],  # collision!
                "introduced": "Act1/Ch2",
            },
        },
        "relationships": [],
    }
    result = validate_relationships(data)
    assert not result.ok
    assert any("alias" in e.lower() for e in result.errors)


def test_validate_catches_temporal_overlap():
    """Two active rels of the same type between same entities should flag overlap."""
    data = {
        "rel_vocabulary": {"negative": ["fears"], "positive": [], "neutral": [], "causal": []},
        "entities": {},
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "fears",
                "context": "x", "valid_from": "Act1/Ch1", "valid_to": None,
                "confidence": "high", "source": "canon/file.md",
            },
            {
                "id": "rel_002", "from": "a", "to": "b", "rel": "fears",
                "context": "y", "valid_from": "Act1/Ch3", "valid_to": None,
                "confidence": "high", "source": "canon/file.md",
            },
        ],
    }
    result = validate_relationships(data)
    assert not result.ok
    assert any("overlap" in e.lower() for e in result.errors)


def test_validate_checks_source_citation_format():
    """Source field must match canon path format."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {},
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "trusts",
                "context": "x", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "bible/old-file.md",  # bad format!
            },
        ],
    }
    result = validate_relationships(data)
    assert not result.ok
    assert any("source" in e.lower() for e in result.errors)


def test_validate_passes_clean_data(sample_rels):
    """The sample fixture has a known temporal overlap (rel_002 and rel_005 both fears from marcus to zone_3).
    We test with cleaned data."""
    data = copy.deepcopy(sample_rels)
    # Fix: the sample has overlapping fears rels AND broken supersession (rel_004 supersedes rel_001 but rel_001.superseded_by is null)
    # Fix supersession: set rel_001.superseded_by = rel_004
    for r in data["relationships"]:
        if r["id"] == "rel_001":
            r["superseded_by"] = "rel_004"
    # Fix temporal overlap: set rel_005.valid_to so it doesn't overlap with rel_002
    # rel_005 already has valid_to: Act1/Ch9, rel_002 starts Act1/Ch2 — they overlap from Act1/Ch2 to Act1/Ch9
    # Remove rel_005 to make clean
    data["relationships"] = [r for r in data["relationships"] if r["id"] != "rel_005"]
    result = validate_relationships(data)
    assert result.ok, f"Errors: {result.errors}"


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


def test_validate_cli_valid(tmp_path):
    """--validate on a clean file should exit 0."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {
            "a": {"type": "character", "aliases": ["A"], "introduced": "L1/concept"},
        },
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "a", "rel": "trusts",
                "context": "self", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "canon/file.md",
            },
        ],
    }
    f = tmp_path / "rels.yaml"
    f.write_text(yaml.dump(data, default_flow_style=False))
    result = subprocess.run(
        [sys.executable, "scripts/relationship_query.py", "--validate", "--file", str(f)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0


def test_validate_cli_invalid(tmp_path):
    """--validate on a bad file should exit non-zero."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {},
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "INVALID_TERM",
                "context": "x", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "canon/file.md",
            },
        ],
    }
    f = tmp_path / "bad_rels.yaml"
    f.write_text(yaml.dump(data, default_flow_style=False))
    result = subprocess.run(
        [sys.executable, "scripts/relationship_query.py", "--validate", "--file", str(f)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode != 0


def test_query_cli(tmp_path):
    """query subcommand should output results."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {
            "a": {"type": "character", "aliases": ["A"], "introduced": "L1/concept"},
            "b": {"type": "character", "aliases": ["B"], "introduced": "L1/concept"},
        },
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "trusts",
                "context": "test", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "canon/file.md",
            },
        ],
    }
    f = tmp_path / "rels.yaml"
    f.write_text(yaml.dump(data, default_flow_style=False))
    result = subprocess.run(
        [sys.executable, "scripts/relationship_query.py", "query",
         "--entity", "a", "--file", str(f)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0
    assert "trusts" in result.stdout


def test_render_matrix_cli(tmp_path):
    """render-matrix subcommand should output markdown."""
    data = {
        "rel_vocabulary": {"positive": ["trusts"], "negative": [], "neutral": [], "causal": []},
        "entities": {
            "a": {"type": "character", "aliases": ["A"], "introduced": "L1/concept"},
            "b": {"type": "character", "aliases": ["B"], "introduced": "L1/concept"},
        },
        "relationships": [
            {
                "id": "rel_001", "from": "a", "to": "b", "rel": "trusts",
                "context": "test", "valid_from": "Act1/Ch1", "confidence": "high",
                "source": "canon/file.md",
            },
        ],
    }
    f = tmp_path / "rels.yaml"
    f.write_text(yaml.dump(data, default_flow_style=False))
    result = subprocess.run(
        [sys.executable, "scripts/relationship_query.py", "render-matrix", "--file", str(f)],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent),
    )
    assert result.returncode == 0
    assert "| From" in result.stdout
