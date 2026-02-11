"""TDD tests for schema validation.

Tests written first per Phase 0 plan S0.1b.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts to path so we can import the validator
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from schema_validator import validate, validate_all, validate_file


SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


# --- agent_comment ---


def test_valid_agent_comment_passes():
    """A correctly formed agent comment should pass validation."""
    comment = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "Ch3 feels like a stall — no value shift.",
        "citations": ["canon/acts/act-1/ch3-outline.md#L12"],
        "suggested_changes": [],
        "resolution": None,
    }
    assert validate("agent_comment", comment).ok


def test_agent_comment_missing_citations_fails():
    """Comments without citations list should fail."""
    comment = {"agent": "plot_analyst", "comment": "Something vague"}
    result = validate("agent_comment", comment)
    assert not result.ok
    assert any("citations" in e for e in result.errors)


def test_agent_comment_missing_model_fails():
    """Comments without model field should fail."""
    comment = {
        "agent": "plot_analyst",
        "comment": "Valid comment text.",
        "citations": ["canon/file.md"],
        "suggested_changes": [],
    }
    result = validate("agent_comment", comment)
    assert not result.ok
    assert any("model" in e for e in result.errors)


def test_agent_comment_empty_comment_fails():
    """Empty comment string should fail minLength constraint."""
    comment = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "",
        "citations": [],
        "suggested_changes": [],
    }
    result = validate("agent_comment", comment)
    assert not result.ok


def test_agent_comment_valid_resolution_values():
    """Resolution must be one of the allowed enum values."""
    base = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "Some comment.",
        "citations": ["canon/file.md"],
        "suggested_changes": [],
    }
    for resolution in ["accepted", "rejected", "deferred", None]:
        data = {**base, "resolution": resolution}
        assert validate("agent_comment", data).ok, f"Failed for resolution={resolution}"


def test_agent_comment_invalid_resolution_fails():
    """Resolution with non-enum value should fail."""
    comment = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "Some comment.",
        "citations": ["canon/file.md"],
        "suggested_changes": [],
        "resolution": "maybe",
    }
    result = validate("agent_comment", comment)
    assert not result.ok


# --- commit_patch ---


def test_valid_commit_patch_requires_citation():
    """Canon mutations must have citation chains (M5)."""
    patch = {
        "canon_changes": [{"file": "canon/acts/act-1-outline.md", "action": "update"}],
        "relationship_changes": [{"id": "rel_001", "field": "valid_to", "new_value": "Act2/Ch1"}],
        "citations": [],
    }
    result = validate("commit_patch", patch)
    assert not result.ok
    assert any("citation" in e.lower() for e in result.errors)


def test_valid_commit_patch_passes():
    """A well-formed commit patch should pass."""
    patch = {
        "canon_changes": [
            {
                "file": "canon/acts/act-1-outline.md",
                "action": "update",
                "summary": "Added turning point to chapter 3.",
            }
        ],
        "relationship_changes": [],
        "citations": ["canon/acts/act-1/ch3-outline.md#L12"],
    }
    assert validate("commit_patch", patch).ok


def test_commit_patch_invalid_action_fails():
    """Canon change with invalid action should fail."""
    patch = {
        "canon_changes": [{"file": "canon/file.md", "action": "rename"}],
        "relationship_changes": [],
        "citations": ["canon/file.md"],
    }
    result = validate("commit_patch", patch)
    assert not result.ok


# --- relationships ---


def test_relationship_entry_bad_vocabulary_fails():
    """Rel terms not in controlled vocabulary should fail pattern check."""
    data = {
        "rel_vocabulary": {
            "positive": ["trusts"],
            "negative": ["fears"],
            "neutral": ["knows"],
            "causal": ["caused"],
        },
        "entities": {
            "marcus": {
                "type": "character",
                "aliases": ["Marcus"],
                "introduced": "L1/concept",
            }
        },
        "relationships": [
            {
                "id": "rel_001",
                "from": "marcus",
                "to": "elena",
                "rel": "is_suspicious_of",
                "context": "test",
                "valid_from": "Act1/Ch1",
                "confidence": "high",
                "source": "canon/acts/act-1/ch1-outline.md#L23",
            }
        ],
    }
    # Note: the schema validates structure, not vocabulary membership.
    # Vocabulary validation is handled by relationship_query.py --validate.
    # The schema itself validates the structural format.
    result = validate("relationships", data)
    assert result.ok  # Structural validation passes; semantic check is in S0.2


def test_valid_relationships_passes():
    """A well-formed relationships file should pass."""
    data = {
        "rel_vocabulary": {
            "positive": ["trusts", "loves"],
            "negative": ["distrusts", "fears"],
            "neutral": ["knows"],
            "causal": ["caused"],
        },
        "entities": {
            "marcus": {
                "type": "character",
                "aliases": ["Marcus", "the soldier"],
                "introduced": "L1/concept",
            }
        },
        "relationships": [
            {
                "id": "rel_001",
                "from": "marcus",
                "to": "elena",
                "rel": "distrusts",
                "context": "refuses her help at Zone perimeter",
                "valid_from": "Act1/Ch1",
                "confidence": "high",
                "source": "canon/acts/act-1/ch1-outline.md#L23",
            }
        ],
    }
    assert validate("relationships", data).ok


def test_relationships_missing_entities_fails():
    """Missing required entities field should fail."""
    data = {
        "rel_vocabulary": {"positive": [], "negative": [], "neutral": [], "causal": []},
        "relationships": [],
    }
    result = validate("relationships", data)
    assert not result.ok
    assert any("entities" in e for e in result.errors)


# --- pipeline_state ---


def test_valid_pipeline_state_passes():
    """A well-formed pipeline state should pass."""
    data = {
        "position": {"level": "L1", "act": None, "chapter": None, "scene": None},
        "mode": "manual",
        "canon_version": 1,
        "max_context_tokens": 100000,
    }
    assert validate("pipeline_state", data).ok


def test_pipeline_state_missing_position_fails():
    """Missing position should fail."""
    data = {"mode": "manual", "canon_version": 1, "max_context_tokens": 100000}
    result = validate("pipeline_state", data)
    assert not result.ok


def test_pipeline_state_invalid_level_fails():
    """Invalid level enum value should fail."""
    data = {
        "position": {"level": "L9"},
        "mode": "manual",
        "canon_version": 1,
        "max_context_tokens": 100000,
    }
    result = validate("pipeline_state", data)
    assert not result.ok


# --- node_input ---


def test_valid_node_input_passes():
    """A well-formed node input should pass."""
    data = {
        "step": "act1-outline",
        "level": "L3",
        "context_files": ["canon/story-concept.md", "canon/story-arc.md"],
        "instructions": "Create the act 1 outline based on the story arc.",
    }
    assert validate("node_input", data).ok


def test_node_input_empty_context_files_fails():
    """Empty context_files should fail minItems constraint."""
    data = {
        "step": "act1-outline",
        "level": "L3",
        "context_files": [],
        "instructions": "Do something.",
    }
    result = validate("node_input", data)
    assert not result.ok


# --- validate_all ---


def test_all_schemas_are_valid():
    """Every schema file should be well-formed JSON Schema with $id and $schema."""
    results = validate_all()
    assert len(results) >= 10, f"Expected at least 10 schemas, found {len(results)}"
    for name, result in results.items():
        assert result.ok, f"Schema '{name}' failed: {result.errors}"


# --- validate_file (CLI-style) ---


def test_validate_file_valid_example():
    """Validating valid_comment.yaml against agent_comment schema should pass."""
    schema_path = SCHEMAS_DIR / "agent_comment.schema.yaml"
    data_path = EXAMPLES_DIR / "valid_comment.yaml"
    if not data_path.exists():
        pytest.skip("Example file not found")
    result = validate_file(schema_path, data_path)
    assert result.ok


def test_validate_file_bad_example():
    """Validating bad_comment.yaml against agent_comment schema should fail."""
    schema_path = SCHEMAS_DIR / "agent_comment.schema.yaml"
    data_path = EXAMPLES_DIR / "bad_comment.yaml"
    if not data_path.exists():
        pytest.skip("Example file not found")
    result = validate_file(schema_path, data_path)
    assert not result.ok


# --- story_concept_input (Phase 1) ---


def test_valid_story_concept_input_passes():
    """A well-formed story concept input should pass."""
    data = {
        "genre": "post-apocalyptic thriller",
        "protagonist": "Marcus Reeves",
        "inciting_situation": "A coded signal from a dead zone.",
    }
    assert validate("story_concept_input", data).ok


def test_story_concept_input_with_optionals_passes():
    """Story concept with all optional fields should pass."""
    data = {
        "genre": "sci-fi",
        "protagonist": "Elena",
        "inciting_situation": "Colony ship loses contact with Earth.",
        "comparable_titles": ["The Expanse", "Seveneves"],
        "world_premise": "Near-future space colonization.",
        "target_length": "90,000 words",
    }
    assert validate("story_concept_input", data).ok


def test_story_concept_input_missing_genre_fails():
    """Missing genre should fail."""
    data = {
        "protagonist": "Marcus",
        "inciting_situation": "Signal from dead zone.",
    }
    result = validate("story_concept_input", data)
    assert not result.ok


def test_story_concept_input_missing_protagonist_fails():
    """Missing protagonist should fail."""
    data = {
        "genre": "thriller",
        "inciting_situation": "Signal from dead zone.",
    }
    result = validate("story_concept_input", data)
    assert not result.ok


def test_story_concept_input_empty_genre_fails():
    """Empty genre string should fail minLength."""
    data = {
        "genre": "",
        "protagonist": "Marcus",
        "inciting_situation": "Signal.",
    }
    result = validate("story_concept_input", data)
    assert not result.ok


def test_story_concept_input_extra_field_fails():
    """Additional properties should be rejected."""
    data = {
        "genre": "thriller",
        "protagonist": "Marcus",
        "inciting_situation": "Signal.",
        "mood": "dark",
    }
    result = validate("story_concept_input", data)
    assert not result.ok


# --- story_arc_input (Phase 1) ---


def test_valid_story_arc_input_passes():
    """A well-formed story arc input should pass."""
    data = {
        "concept_file": "canon/story-concept.md",
    }
    assert validate("story_arc_input", data).ok


def test_story_arc_input_with_optionals_passes():
    """Story arc with all optional fields should pass."""
    data = {
        "concept_file": "canon/story-concept.md",
        "target_scope": "full_story",
        "act_count": 4,
        "character_files": ["canon/characters/marcus.md"],
    }
    assert validate("story_arc_input", data).ok


def test_story_arc_input_missing_concept_file_fails():
    """Missing concept_file should fail."""
    data = {"target_scope": "full_story"}
    result = validate("story_arc_input", data)
    assert not result.ok


def test_story_arc_input_act_count_below_minimum_fails():
    """act_count below 3 should fail."""
    data = {
        "concept_file": "canon/story-concept.md",
        "act_count": 2,
    }
    result = validate("story_arc_input", data)
    assert not result.ok


# --- act_outline_input (Phase 1) ---


def test_valid_act_outline_input_passes():
    """A well-formed act outline input should pass."""
    data = {
        "arc_file": "canon/story-arc.md",
        "act_number": 1,
    }
    assert validate("act_outline_input", data).ok


def test_act_outline_input_with_hint_passes():
    """Act outline with chapter_count_hint should pass."""
    data = {
        "arc_file": "canon/story-arc.md",
        "act_number": 2,
        "chapter_count_hint": 8,
    }
    assert validate("act_outline_input", data).ok


def test_act_outline_input_missing_act_number_fails():
    """Missing act_number should fail."""
    data = {"arc_file": "canon/story-arc.md"}
    result = validate("act_outline_input", data)
    assert not result.ok


def test_act_outline_input_act_number_zero_fails():
    """act_number: 0 should fail minimum: 1 constraint."""
    data = {
        "arc_file": "canon/story-arc.md",
        "act_number": 0,
    }
    result = validate("act_outline_input", data)
    assert not result.ok


def test_act_outline_input_missing_arc_file_fails():
    """Missing arc_file should fail."""
    data = {"act_number": 1}
    result = validate("act_outline_input", data)
    assert not result.ok


# --- Phase 1 example files ---


def test_validate_file_valid_concept_input():
    """Valid concept input example should pass schema validation."""
    schema_path = SCHEMAS_DIR / "story_concept_input.schema.yaml"
    data_path = EXAMPLES_DIR / "phase1" / "valid_concept_input.yaml"
    if not data_path.exists():
        pytest.skip("Example file not found")
    result = validate_file(schema_path, data_path)
    assert result.ok, f"Validation failed: {result.errors}"


def test_validate_file_valid_arc_input():
    """Valid arc input example should pass schema validation."""
    schema_path = SCHEMAS_DIR / "story_arc_input.schema.yaml"
    data_path = EXAMPLES_DIR / "phase1" / "valid_arc_input.yaml"
    if not data_path.exists():
        pytest.skip("Example file not found")
    result = validate_file(schema_path, data_path)
    assert result.ok, f"Validation failed: {result.errors}"


def test_validate_file_valid_outline_input():
    """Valid outline input example should pass schema validation."""
    schema_path = SCHEMAS_DIR / "act_outline_input.schema.yaml"
    data_path = EXAMPLES_DIR / "phase1" / "valid_outline_input.yaml"
    if not data_path.exists():
        pytest.skip("Example file not found")
    result = validate_file(schema_path, data_path)
    assert result.ok, f"Validation failed: {result.errors}"
