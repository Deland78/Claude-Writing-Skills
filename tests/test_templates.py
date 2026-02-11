"""Tests for L1-L3 template structure and golden example conformance.

Verifies that templates contain all required section headings and that
golden examples stay in sync with the template definitions.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
EXAMPLES_DIR = PROJECT_ROOT / "examples" / "phase1"


def _extract_h2_headings(text: str) -> set[str]:
    """Extract all ## level headings from markdown text."""
    return {m.group(1).strip() for m in re.finditer(r"^##\s+(.+)$", text, re.MULTILINE)}


# ---------------------------------------------------------------------------
# Required headings per template level
# ---------------------------------------------------------------------------

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

L2_REQUIRED_HEADINGS = {
    "Arc Overview",
    "Act Progression",
    "Character Trajectories",
    "Subplot Map",
    "Thematic Pressure Points",
    "Open Questions",
    "Sources",
}

L3_REQUIRED_HEADINGS = {
    "Act Overview",
    "Chapter List",
    "Continuity Touchpoints",
    "Open Questions",
    "Sources",
}


# ---------------------------------------------------------------------------
# Template existence and structure
# ---------------------------------------------------------------------------


def test_story_concept_template_exists():
    """story-concept.template.md must exist."""
    assert (TEMPLATES_DIR / "story-concept.template.md").exists()


def test_story_arc_template_exists():
    """story-arc.template.md must exist."""
    assert (TEMPLATES_DIR / "story-arc.template.md").exists()


def test_act_outline_template_exists():
    """act-outline.template.md must exist."""
    assert (TEMPLATES_DIR / "act-outline.template.md").exists()


def test_story_concept_template_has_required_headings():
    """L1 template must contain all required ## headings."""
    content = (TEMPLATES_DIR / "story-concept.template.md").read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L1_REQUIRED_HEADINGS - headings
    assert not missing, f"L1 template missing headings: {missing}"


def test_story_arc_template_has_required_headings():
    """L2 template must contain all required ## headings."""
    content = (TEMPLATES_DIR / "story-arc.template.md").read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L2_REQUIRED_HEADINGS - headings
    assert not missing, f"L2 template missing headings: {missing}"


def test_act_outline_template_has_required_headings():
    """L3 template must contain all required ## headings."""
    content = (TEMPLATES_DIR / "act-outline.template.md").read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L3_REQUIRED_HEADINGS - headings
    assert not missing, f"L3 template missing headings: {missing}"


def test_all_templates_have_level1_heading():
    """Every template must start with a # level-1 heading."""
    for name in ["story-concept", "story-arc", "act-outline"]:
        path = TEMPLATES_DIR / f"{name}.template.md"
        content = path.read_text(encoding="utf-8")
        assert re.search(r"^# .+", content, re.MULTILINE), f"{name} template missing # heading"


def test_all_templates_use_comment_placeholders():
    """Templates should use <!-- --> comment syntax for placeholders."""
    for name in ["story-concept", "story-arc", "act-outline"]:
        path = TEMPLATES_DIR / f"{name}.template.md"
        content = path.read_text(encoding="utf-8")
        assert "<!--" in content, f"{name} template has no <!-- --> placeholders"


# ---------------------------------------------------------------------------
# Golden example conformance
# ---------------------------------------------------------------------------


def test_l1_golden_example_exists():
    """L1 golden example must exist."""
    assert (EXAMPLES_DIR / "l1_story-concept.example.md").exists()


def test_l2_golden_example_exists():
    """L2 golden example must exist."""
    assert (EXAMPLES_DIR / "l2_story-arc.example.md").exists()


def test_l3_golden_example_exists():
    """L3 golden example must exist."""
    assert (EXAMPLES_DIR / "l3_act-outline.example.md").exists()


def test_l1_golden_example_has_required_headings():
    """L1 golden example must contain all required ## headings."""
    content = (EXAMPLES_DIR / "l1_story-concept.example.md").read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L1_REQUIRED_HEADINGS - headings
    assert not missing, f"L1 example missing headings: {missing}"


def test_l2_golden_example_has_required_headings():
    """L2 golden example must contain all required ## headings."""
    content = (EXAMPLES_DIR / "l2_story-arc.example.md").read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L2_REQUIRED_HEADINGS - headings
    assert not missing, f"L2 example missing headings: {missing}"


def test_l3_golden_example_has_required_headings():
    """L3 golden example must contain all required ## headings."""
    content = (EXAMPLES_DIR / "l3_act-outline.example.md").read_text(encoding="utf-8")
    headings = _extract_h2_headings(content)
    missing = L3_REQUIRED_HEADINGS - headings
    assert not missing, f"L3 example missing headings: {missing}"


def test_golden_examples_are_nonempty():
    """Golden examples should have substantial content (not just headings)."""
    for name in [
        "l1_story-concept.example.md",
        "l2_story-arc.example.md",
        "l3_act-outline.example.md",
    ]:
        path = EXAMPLES_DIR / name
        content = path.read_text(encoding="utf-8")
        # At least 500 chars of content beyond headings
        assert len(content) > 500, f"{name} is too short ({len(content)} chars)"
