"""Tests for mob governance rules (P2A.4).

Verifies citation enforcement documentation, schema support for
citation_status, and governance configuration in pipeline state.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from schema_validator import validate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
AGENTS_DIR = PROJECT_ROOT / "agents"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"


# ---------------------------------------------------------------------------
# Citation enforcement document
# ---------------------------------------------------------------------------


def test_citation_enforcement_doc_exists():
    """docs/citation_enforcement.md must exist."""
    assert (DOCS_DIR / "citation_enforcement.md").exists()


def test_citation_enforcement_doc_has_cited_rule():
    """Citation enforcement doc must describe 'cited' status."""
    content = (DOCS_DIR / "citation_enforcement.md").read_text(encoding="utf-8")
    assert "cited" in content.lower()
    assert "canon/" in content


def test_citation_enforcement_doc_has_advisory_rule():
    """Citation enforcement doc must describe 'advisory' status."""
    content = (DOCS_DIR / "citation_enforcement.md").read_text(encoding="utf-8")
    assert "advisory" in content.lower()


def test_citation_enforcement_doc_has_override_rule():
    """Citation enforcement doc must describe human override for advisory comments."""
    content = (DOCS_DIR / "citation_enforcement.md").read_text(encoding="utf-8")
    assert "override" in content.lower()


def test_citation_enforcement_doc_references_schema():
    """Citation enforcement doc should reference the agent_comment schema."""
    content = (DOCS_DIR / "citation_enforcement.md").read_text(encoding="utf-8")
    assert "agent_comment" in content


def test_citation_enforcement_doc_references_mob_protocol():
    """Citation enforcement doc should reference the mob protocol."""
    content = (DOCS_DIR / "citation_enforcement.md").read_text(encoding="utf-8")
    assert "mob_protocol" in content


# ---------------------------------------------------------------------------
# Schema: citation_status in agent_comment
# ---------------------------------------------------------------------------


def test_citation_status_cited_passes():
    """agent_comment with citation_status 'cited' and non-empty citations should pass."""
    comment = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "Act 2A lacks a pinch point after the midpoint.",
        "citations": ["canon/story-arc.md#L45"],
        "suggested_changes": [],
        "citation_status": "cited",
        "resolution": "accepted",
    }
    assert validate("agent_comment", comment).ok


def test_citation_status_advisory_passes():
    """agent_comment with citation_status 'advisory' and empty citations should pass."""
    comment = {
        "agent": "depth_partner",
        "model": "claude-haiku",
        "comment": "Theme feels underdeveloped in Act 1.",
        "citations": [],
        "suggested_changes": [],
        "citation_status": "advisory",
        "resolution": "deferred",
    }
    assert validate("agent_comment", comment).ok


def test_citation_status_invalid_value_fails():
    """agent_comment with unknown citation_status should fail."""
    comment = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "Some observation.",
        "citations": [],
        "suggested_changes": [],
        "citation_status": "unknown",
    }
    result = validate("agent_comment", comment)
    assert not result.ok


def test_citation_status_is_optional():
    """citation_status is not in required fields — omission should still pass."""
    comment = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "Valid comment.",
        "citations": ["canon/file.md"],
        "suggested_changes": [],
    }
    assert validate("agent_comment", comment).ok


def test_cited_with_empty_citations_is_logically_inconsistent():
    """Cited status with empty citations is schema-valid but logically wrong.

    The schema does not enforce the logical relationship between citations
    array contents and citation_status — that is the Lead Editor's
    responsibility at runtime. This test documents the expectation.
    """
    comment = {
        "agent": "plot_analyst",
        "model": "claude-haiku",
        "comment": "Some claim.",
        "citations": [],
        "suggested_changes": [],
        "citation_status": "cited",
    }
    # Schema allows it (no cross-field validation), but runtime should catch this
    result = validate("agent_comment", comment)
    assert result.ok  # Structural validation passes


# ---------------------------------------------------------------------------
# Governance config in pipeline state
# ---------------------------------------------------------------------------


def test_pipeline_state_mob_config_validates():
    """Pipeline state with mob_config should pass validation."""
    data = {
        "position": {"level": "L1", "act": None, "chapter": None, "scene": None},
        "mode": "manual",
        "canon_version": 1,
        "max_context_tokens": 100000,
        "mob_config": {
            "max_rounds": 3,
            "budget_cap_usd": 1.0,
            "diminishing_return_threshold": 0,
        },
    }
    assert validate("pipeline_state", data).ok


def test_pipeline_state_mob_config_max_rounds_minimum():
    """max_rounds must be at least 1."""
    data = {
        "position": {"level": "L1"},
        "mode": "manual",
        "canon_version": 1,
        "max_context_tokens": 100000,
        "mob_config": {
            "max_rounds": 0,
        },
    }
    result = validate("pipeline_state", data)
    assert not result.ok


def test_pipeline_state_mob_config_budget_cap_non_negative():
    """budget_cap_usd must be >= 0."""
    data = {
        "position": {"level": "L1"},
        "mode": "manual",
        "canon_version": 1,
        "max_context_tokens": 100000,
        "mob_config": {
            "budget_cap_usd": -0.5,
        },
    }
    result = validate("pipeline_state", data)
    assert not result.ok


def test_live_pipeline_state_has_mob_config():
    """The actual .pipeline-state.yaml should contain mob_config."""
    state_path = PROJECT_ROOT / ".pipeline-state.yaml"
    assert state_path.exists(), ".pipeline-state.yaml not found"
    data = yaml.safe_load(state_path.read_text(encoding="utf-8"))
    assert "mob_config" in data
    assert "max_rounds" in data["mob_config"]
    assert "diminishing_return_threshold" in data["mob_config"]


# ---------------------------------------------------------------------------
# Lead Editor governance references
# ---------------------------------------------------------------------------


def test_lead_editor_references_citation_enforcement():
    """Lead Editor agent definition should reference citation enforcement."""
    content = (AGENTS_DIR / "lead-editor.md").read_text(encoding="utf-8")
    assert "citation" in content.lower()


def test_lead_editor_references_round_limit():
    """Lead Editor should reference round limit governance."""
    content = (AGENTS_DIR / "lead-editor.md").read_text(encoding="utf-8")
    assert "max_rounds" in content or "round limit" in content.lower()


def test_lead_editor_references_diminishing_returns():
    """Lead Editor should reference diminishing returns governance."""
    content = (AGENTS_DIR / "lead-editor.md").read_text(encoding="utf-8")
    assert "diminishing" in content.lower()


# ---------------------------------------------------------------------------
# Mob protocol governance section
# ---------------------------------------------------------------------------


def test_mob_protocol_has_governance_checks():
    """mob_protocol.md should describe governance checks."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "Governance" in content
    assert "max_rounds" in content


def test_mob_protocol_references_citation_enforcement():
    """mob_protocol.md should reference citation_enforcement.md."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "citation_enforcement.md" in content


def test_mob_protocol_has_termination_rules():
    """mob_protocol.md should describe termination conditions."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "diminishing" in content.lower() or "Diminishing" in content
    assert "Round limit" in content or "round limit" in content.lower()
