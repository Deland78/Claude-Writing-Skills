"""Tests for the mob session skill and protocol (P2A.3).

Verifies skill file structure, protocol documentation, and required
references. Does NOT test mob session execution quality.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / ".claude" / "skills" / "mob-session"
DOCS_DIR = PROJECT_ROOT / "docs"
AGENTS_DIR = PROJECT_ROOT / "agents"


# ---------------------------------------------------------------------------
# Skill file structure
# ---------------------------------------------------------------------------


def test_mob_session_skill_exists():
    """SKILL.md must exist in the mob-session skill directory."""
    assert (SKILL_DIR / "SKILL.md").exists()


def test_mob_session_skill_has_yaml_frontmatter():
    """SKILL.md must have YAML frontmatter with name and description."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---")
    parts = content.split("---", 2)
    assert len(parts) >= 3
    frontmatter = yaml.safe_load(parts[1])
    assert "name" in frontmatter
    assert "description" in frontmatter


def test_mob_session_skill_name():
    """SKILL.md frontmatter name should be 'Mob Session'."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    parts = content.split("---", 2)
    frontmatter = yaml.safe_load(parts[1])
    assert frontmatter["name"] == "Mob Session"


# ---------------------------------------------------------------------------
# Protocol references in skill
# ---------------------------------------------------------------------------


def test_skill_references_agents_directory():
    """SKILL.md should reference the agents/ directory."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "agents/" in content


def test_skill_documents_all_four_phases():
    """SKILL.md should document all 4 protocol phases."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "Phase 1" in content
    assert "Phase 2" in content
    assert "Phase 3" in content
    assert "Phase 4" in content


def test_skill_includes_role_switch_separator():
    """SKILL.md should include the role-switch separator convention."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "Now speaking as" in content


def test_skill_references_context_loader():
    """SKILL.md should reference context_loader for context loading."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "context_loader" in content


def test_skill_references_governance():
    """SKILL.md should reference governance rules."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "governance" in content.lower() or "Governance" in content


def test_skill_references_citation_enforcement():
    """SKILL.md should reference citation enforcement."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "citation" in content.lower()


def test_skill_references_trace_renderer():
    """SKILL.md should reference trace_renderer for session logging."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "trace_renderer" in content


def test_skill_documents_agent_activation_table():
    """SKILL.md should include an agent activation table by level."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    # Should show which agents are active at which levels
    assert "L1" in content and "L5" in content
    assert "active" in content.lower() and "off" in content.lower()


# ---------------------------------------------------------------------------
# Protocol document
# ---------------------------------------------------------------------------


def test_protocol_doc_exists():
    """docs/mob_protocol.md must exist."""
    assert (DOCS_DIR / "mob_protocol.md").exists()


def test_protocol_doc_has_four_phases():
    """Protocol doc should describe all 4 phases."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "Phase 1" in content
    assert "Phase 2" in content
    assert "Phase 3" in content
    assert "Phase 4" in content


def test_protocol_doc_has_turn_order():
    """Protocol doc should define the agent turn order."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "Plot Analyst" in content
    assert "Character Specialist" in content
    assert "Depth Partner" in content
    assert "Continuity Agent" in content
    assert "Prose Crafter" in content


def test_protocol_doc_has_governance_section():
    """Protocol doc should include governance rules."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "Governance" in content
    assert "max_rounds" in content or "round limit" in content.lower()


def test_protocol_doc_references_citation_enforcement():
    """Protocol doc should reference citation enforcement."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "citation_enforcement.md" in content


def test_protocol_doc_has_role_switch_convention():
    """Protocol doc should document role-switch separators."""
    content = (DOCS_DIR / "mob_protocol.md").read_text(encoding="utf-8")
    assert "Now speaking as" in content
