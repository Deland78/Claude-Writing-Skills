"""Tests for the story-concept skill (P1.3).

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
SKILL_DIR = PROJECT_ROOT / ".claude" / "skills" / "story-concept"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
EXAMPLES_DIR = PROJECT_ROOT / "examples" / "phase1"


L1_REQUIRED_HEADINGS = {
    "Premise",
    "Genre",
    "Controlling Idea",
    "Central Dramatic Question",
    "Stakes",
    "Story Promise",
    "Point of View",
    "Setting",
    "Target Scope",
    "Sources",
}


def _extract_h2_headings(text: str) -> set[str]:
    return {m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)}


# ---------------------------------------------------------------------------
# Skill file structure
# ---------------------------------------------------------------------------


def test_skill_file_exists():
    """SKILL.md must exist in the story-concept skill directory."""
    assert (SKILL_DIR / "SKILL.md").exists()


def test_skill_has_yaml_frontmatter():
    """SKILL.md must have YAML frontmatter with name and description."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    # Extract frontmatter
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have opening and closing --- for frontmatter"
    frontmatter = yaml.safe_load(parts[1])
    assert "name" in frontmatter, "Frontmatter must include 'name'"
    assert "description" in frontmatter, "Frontmatter must include 'description'"


def test_skill_references_template():
    """SKILL.md should reference the story-concept template."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "story-concept.template.md" in content


def test_skill_documents_state_update():
    """SKILL.md should document the pipeline state transition."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "State Update" in content or "state update" in content.lower()


def test_skill_references_story_promise():
    """SKILL.md should reference the story-promise framework."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "story-promise" in content.lower() or "story promise" in content.lower()


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_valid_concept_input_passes_schema():
    """A valid story concept input should pass schema validation."""
    data = {
        "genre": "thriller",
        "protagonist": "Marcus Reeves",
        "inciting_situation": "A signal from a dead zone.",
    }
    assert validate("story_concept_input", data).ok


def test_concept_input_missing_required_field_fails():
    """Missing required fields should fail validation."""
    # Missing genre
    data = {
        "protagonist": "Marcus",
        "inciting_situation": "Signal.",
    }
    assert not validate("story_concept_input", data).ok


# ---------------------------------------------------------------------------
# Template conformance (using golden example as proxy for skill output)
# ---------------------------------------------------------------------------


def test_template_exists():
    """The story-concept template must exist."""
    assert (TEMPLATES_DIR / "story-concept.template.md").exists()


def test_golden_example_conforms_to_template():
    """The L1 golden example must contain all required template headings."""
    example_path = EXAMPLES_DIR / "l1_story-concept.example.md"
    if not example_path.exists():
        pytest.skip("Golden example not found")
    content = example_path.read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L1_REQUIRED_HEADINGS - headings
    assert not missing, f"Golden example missing headings: {missing}"


def test_golden_example_has_no_placeholder_comments():
    """The golden example should not contain <!-- --> placeholder comments."""
    example_path = EXAMPLES_DIR / "l1_story-concept.example.md"
    if not example_path.exists():
        pytest.skip("Golden example not found")
    content = example_path.read_text(encoding="utf-8")
    assert "<!--" not in content, "Golden example still contains placeholder comments"


def test_output_path_is_correct():
    """Skill should write to canon/story-concept.md."""
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "canon/story-concept.md" in content
