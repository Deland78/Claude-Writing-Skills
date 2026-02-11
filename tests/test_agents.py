"""Tests for agent role definitions (P2A.1).

Verifies all agent files exist, follow the defined format convention,
and conform to the shared contract. Does NOT test agent output quality.
"""

from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"
DOCS_DIR = PROJECT_ROOT / "docs"

AGENTS = [
    "lead-editor",
    "plot-analyst",
    "character-specialist",
    "depth-partner",
    "continuity-agent",
    "prose-crafter",
]

SPECIALIST_AGENTS = [a for a in AGENTS if a != "lead-editor"]


def load_agent(name: str) -> str:
    return (AGENTS_DIR / f"{name}.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Agent file existence
# ---------------------------------------------------------------------------


def test_agents_directory_exists():
    """The agents/ directory must exist."""
    assert AGENTS_DIR.exists() and AGENTS_DIR.is_dir()


@pytest.mark.parametrize("agent", AGENTS)
def test_agent_file_exists(agent: str):
    """Each agent definition file must exist."""
    assert (AGENTS_DIR / f"{agent}.md").exists(), f"Missing agents/{agent}.md"


# ---------------------------------------------------------------------------
# Specialist required sections
# ---------------------------------------------------------------------------

REQUIRED_SPECIALIST_HEADINGS = [
    "## Scope",
    "## Out of Scope",
    "## Active Levels",
    "## Evidence Rule",
    "## Escalation Rule",
    "## Model Tier",
]


@pytest.mark.parametrize("agent", SPECIALIST_AGENTS)
def test_specialist_has_required_sections(agent: str):
    """Each specialist agent must have all required section headings."""
    content = load_agent(agent)
    for heading in REQUIRED_SPECIALIST_HEADINGS:
        assert heading in content, f"{agent} missing {heading}"


@pytest.mark.parametrize("agent", AGENTS)
def test_agent_has_role_section(agent: str):
    """Every agent (including Lead Editor) must have a Role section."""
    content = load_agent(agent)
    assert "## Role" in content, f"{agent} missing ## Role"


@pytest.mark.parametrize("agent", AGENTS)
def test_agent_has_prompt_section(agent: str):
    """Every agent must have a Prompt section."""
    content = load_agent(agent)
    assert "## Prompt" in content, f"{agent} missing ## Prompt"


# ---------------------------------------------------------------------------
# Specific agent constraints
# ---------------------------------------------------------------------------


def test_prose_crafter_restricted_to_l4_l5():
    """Prose Crafter should only be active at L4 and L5."""
    content = load_agent("prose-crafter")
    assert "L4" in content and "L5" in content
    assert "## Active Levels" in content


def test_continuity_agent_restricted_to_l3_plus():
    """Continuity Agent should be active at L3, L4, L5."""
    content = load_agent("continuity-agent")
    assert "L3" in content
    assert "## Active Levels" in content


def test_depth_partner_restricted_to_l1_l3():
    """Depth Partner should be active at L1, L2, L3."""
    content = load_agent("depth-partner")
    assert "L1" in content and "L3" in content
    assert "## Active Levels" in content


def test_lead_editor_has_protocol_reference():
    """Lead Editor must reference the protocol."""
    content = load_agent("lead-editor")
    assert "protocol" in content.lower()


def test_lead_editor_has_governance_section():
    """Lead Editor must document governance enforcement."""
    content = load_agent("lead-editor")
    assert "governance" in content.lower() or "Governance" in content


# ---------------------------------------------------------------------------
# Citation rule conformance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agent", SPECIALIST_AGENTS)
def test_specialist_references_canon_citation(agent: str):
    """Each specialist must reference canon/ file citation in Evidence Rule."""
    content = load_agent(agent)
    assert "canon/" in content, f"{agent} missing canon/ file citation reference"


@pytest.mark.parametrize("agent", SPECIALIST_AGENTS)
def test_specialist_mentions_advisory(agent: str):
    """Each specialist should mention advisory tagging for uncited claims."""
    content = load_agent(agent)
    assert "advisory" in content.lower(), f"{agent} missing advisory tagging reference"


# ---------------------------------------------------------------------------
# Contract document
# ---------------------------------------------------------------------------


def test_agent_contract_doc_exists():
    """docs/agent_contract.md must exist."""
    assert (DOCS_DIR / "agent_contract.md").exists()


def test_agent_contract_has_citation_rule():
    """Contract doc must contain citation rule."""
    content = (DOCS_DIR / "agent_contract.md").read_text(encoding="utf-8")
    assert "Citation" in content or "citation" in content


def test_agent_contract_has_role_boundaries():
    """Contract doc must contain role boundary rules."""
    content = (DOCS_DIR / "agent_contract.md").read_text(encoding="utf-8")
    assert "Role Boundaries" in content or "role boundaries" in content.lower()
