"""Tests for the story-arc-builder skill (P1.4).

Verifies skill file structure, schema validation, and template conformance
of mock outputs. Does NOT test LLM output quality.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from schema_validator import validate


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / ".claude" / "skills" / "story-arc-builder"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
EXAMPLES_DIR = PROJECT_ROOT / "examples" / "phase1"


L2_REQUIRED_HEADINGS = {
    "Arc Overview",
    "Act Progression",
    "Character Trajectories",
    "Subplot Map",
    "Thematic Pressure Points",
    "Open Questions",
    "Sources",
}


def _extract_h2_headings(text: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)}


# ---------------------------------------------------------------------------
# Skill file structure
# ---------------------------------------------------------------------------


def test_skill_file_exists():
    """SKILL.md must exist in the story-arc-builder skill directory."""
    assert (SKILL_DIR / "SKILL.md").exists()


def test_skill_has_yaml_frontmatter():
    """SKILL.md must have YAML frontmatter with name and description."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---")
    parts = content.split("---", 2)
    assert len(parts) >= 3
    frontmatter = yaml.safe_load(parts[1])
    assert "name" in frontmatter
    assert "description" in frontmatter


def test_skill_references_template():
    """SKILL.md should reference the story-arc template."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "story-arc.template.md" in content


def test_skill_documents_state_update():
    """SKILL.md should document the pipeline state transition."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "State Update" in content or "state update" in content.lower()


def test_skill_requires_concept_file():
    """SKILL.md should reference canon/story-concept.md as required input."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "canon/story-concept.md" in content


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_valid_arc_input_passes_schema():
    """A valid story arc input should pass schema validation."""
    data = {"concept_file": "canon/story-concept.md"}
    assert validate("story_arc_input", data).ok


def test_arc_input_missing_concept_file_fails():
    """Missing concept_file should fail validation."""
    data = {"target_scope": "full_story"}
    assert not validate("story_arc_input", data).ok


def test_arc_input_invalid_act_count_fails():
    """act_count below minimum should fail."""
    data = {"concept_file": "canon/story-concept.md", "act_count": 1}
    assert not validate("story_arc_input", data).ok


# ---------------------------------------------------------------------------
# Template conformance (using golden example as proxy)
# ---------------------------------------------------------------------------


def test_template_exists():
    """The story-arc template must exist."""
    assert (TEMPLATES_DIR / "story-arc.template.md").exists()


def test_golden_example_conforms_to_template():
    """The L2 golden example must contain all required template headings."""
    example_path = EXAMPLES_DIR / "l2_story-arc.example.md"
    if not example_path.exists():
        pytest.skip("Golden example not found")
    content = example_path.read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L2_REQUIRED_HEADINGS - headings
    assert not missing, f"Golden example missing headings: {missing}"


def test_golden_example_has_no_placeholder_comments():
    """The golden example should not contain <!-- --> placeholder comments."""
    example_path = EXAMPLES_DIR / "l2_story-arc.example.md"
    if not example_path.exists():
        pytest.skip("Golden example not found")
    content = example_path.read_text(encoding="utf-8")
    assert "<!--" not in content, "Golden example still contains placeholder comments"


def test_output_path_is_correct():
    """Skill should write to canon/story-arc.md."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "canon/story-arc.md" in content
