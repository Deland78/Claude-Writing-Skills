"""Automated regression test for stale bible/ references.

Ensures that no skill files, CLAUDE.md, or general docs still reference
the old bible/ directory after the Phase 0 migration.
"""

from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent


# Files that legitimately describe the migration itself — allowed to mention bible/.
_MIGRATION_DOCS = {
    "implementation_plan.md",
    "phase0_detailed_plan.md",
    "phase1_detailed_plan.md",
    "phase1_acceptance_checklist.md",
    "walkthrough.md",
    "task.md",
    "migrate_bible_to_canon.py",
    "test_migration.py",
    "test_no_bible_refs.py",  # this file itself
}


def _is_migration_doc(path: Path) -> bool:
    return path.name in _MIGRATION_DOCS


def test_no_bible_references_in_skills():
    """No skill file should contain 'bible/' references after migration."""
    skills_dir = PROJECT_ROOT / ".claude" / "skills"
    if not skills_dir.exists():
        pytest.skip("No .claude/skills directory found")
    for skill_file in skills_dir.rglob("*.md"):
        content = skill_file.read_text(encoding="utf-8")
        assert "bible/" not in content.lower(), f"Stale bible/ ref in {skill_file}"


def test_no_bible_references_in_claude_md():
    """CLAUDE.md should not reference bible/."""
    claude_md = PROJECT_ROOT / "CLAUDE.md"
    if not claude_md.exists():
        pytest.skip("No CLAUDE.md found")
    content = claude_md.read_text(encoding="utf-8")
    assert "bible/" not in content.lower(), "Stale bible/ ref in CLAUDE.md"


def test_no_bible_references_in_docs():
    """docs/ markdown files should not reference bible/ (excluding migration docs)."""
    docs_dir = PROJECT_ROOT / "docs"
    if not docs_dir.exists():
        pytest.skip("No docs/ directory found")
    for path in docs_dir.rglob("*.md"):
        if _is_migration_doc(path):
            continue
        content = path.read_text(encoding="utf-8")
        assert "bible/" not in content.lower(), f"Stale bible/ ref in {path}"


def test_no_bible_references_in_canon():
    """canon/ files should not reference bible/."""
    canon_dir = PROJECT_ROOT / "canon"
    if not canon_dir.exists():
        pytest.skip("No canon/ directory found")
    for path in canon_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        assert "bible/" not in content.lower(), f"Stale bible/ ref in {path}"


def test_no_bible_references_in_templates():
    """templates/ should not reference bible/."""
    templates_dir = PROJECT_ROOT / "templates"
    if not templates_dir.exists():
        pytest.skip("No templates/ directory found")
    for path in templates_dir.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        assert "bible/" not in content.lower(), f"Stale bible/ ref in {path}"
