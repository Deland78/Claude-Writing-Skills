"""TDD tests for the bible-to-canon migration script.

Tests written first per Phase 0 plan S0.3.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from migrate_bible_to_canon import MigrationError, run_migration


def create_test_repo(tmp_path: Path) -> None:
    """Build a minimal test repo structure that mirrors the real project."""
    # bible/
    bible = tmp_path / "bible"
    bible.mkdir()
    (bible / "story-bible.md").write_text("# Story Bible\nThe main story bible content.\n")
    (bible / "world-rules.md").write_text("# World Rules\nMagic system details.\n")
    (bible / "scene-tracker.md").write_text("# Scene Tracker\n| Scene | Status |\n| 1 | done |\n")

    # canon/
    canon = tmp_path / "canon"
    canon.mkdir()
    (canon / "index.md").write_text("# Canon Index\n## Modules\n- timeline.md\n")
    (canon / "timeline.md").write_text("# Canon Timeline\n\nTrack immutable event ordering.\n")
    (canon / "Entity-relationship-matrix.md").write_text("# Entity Matrix\n| From | To |\n")

    # canon/world/
    world = canon / "world"
    world.mkdir()
    (world / "README.md").write_text("# World\nPlaceholder.\n")

    # canon/characters/, canon/tech/, canon/themes/ (with READMEs)
    for d in ["characters", "tech", "themes"]:
        sub = canon / d
        sub.mkdir()
        (sub / "README.md").write_text(f"# {d.title()}\nPlaceholder.\n")

    # canon/style-samples/
    samples = canon / "style-samples"
    samples.mkdir()
    (samples / "sample-01.md").write_text("# Sample\nSome prose.\n")

    # .claude/skills/ with bible references
    skills_dir = tmp_path / ".claude" / "skills"
    for skill_name in ["continuity-callback", "scene-draft", "character-truth", "scene-architect"]:
        skill_path = skills_dir / skill_name
        skill_path.mkdir(parents=True, exist_ok=True)
        if skill_name == "continuity-callback":
            (skill_path / "SKILL.md").write_text(
                "# Continuity Callback\n"
                "Validate continuity consistent with the book bible.\n"
                "Required: chapter_draft, book_bible_or_notes, scene_tracker\n"
                "References: bible/story-bible.md, bible/scene-tracker.md\n"
            )
        elif skill_name == "scene-draft":
            (skill_path / "SKILL.md").write_text(
                "# Scene Draft\n"
                "World Rules: bible/world-rules.md\n"
            )
        elif skill_name == "character-truth":
            (skill_path / "SKILL.md").write_text(
                "# Character Truth\n"
                "Optional: character_bible\n"
            )
        elif skill_name == "scene-architect":
            (skill_path / "SKILL.md").write_text(
                "# Scene Architect\n"
                "Optional: character_bible\n"
            )

    # CLAUDE.md with bible references
    (tmp_path / "CLAUDE.md").write_text(
        "# Project Guide\n"
        "## Key Directories\n"
        "- `bible/`: Active story reference documents\n"
        "- `characters/`: Character profiles\n"
        "## Foundation Setup\n"
        "1. `bible/story-bible.md`\n"
        "2. `bible/world-rules.md`\n"
        "3. `bible/scene-tracker.md`\n"
    )

    # docs/ directory
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "walkthrough.md").write_text("# Walkthrough\nNo bible refs here.\n")


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------


def test_dry_run_produces_mapping_report(tmp_path):
    """--dry-run should list all planned moves without touching files."""
    create_test_repo(tmp_path)
    report = run_migration(tmp_path, dry_run=True)
    assert "story-bible.md" in report
    assert "canon/world/story-bible.md" in report
    assert (tmp_path / "bible" / "story-bible.md").exists()  # NOT moved


def test_dry_run_does_not_modify_files(tmp_path):
    """--dry-run should leave all files untouched."""
    create_test_repo(tmp_path)
    claude_before = (tmp_path / "CLAUDE.md").read_text()
    run_migration(tmp_path, dry_run=True)
    claude_after = (tmp_path / "CLAUDE.md").read_text()
    assert claude_before == claude_after


# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------


def test_execute_moves_files(tmp_path):
    """--execute should move files and update refs."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    assert (tmp_path / "canon" / "world" / "story-bible.md").exists()
    assert (tmp_path / "canon" / "world" / "world-rules.md").exists()
    assert not (tmp_path / "bible" / "story-bible.md").exists()
    assert not (tmp_path / "bible" / "world-rules.md").exists()


def test_execute_merges_scene_tracker(tmp_path):
    """scene-tracker.md content should be merged into timeline.md."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    timeline = (tmp_path / "canon" / "timeline.md").read_text()
    assert "Track immutable event ordering" in timeline  # existing stub
    assert "Scene Tracker" in timeline or "scene" in timeline.lower()


def test_execute_deletes_entity_matrix(tmp_path):
    """Entity-relationship-matrix.md should be deleted."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    assert not (tmp_path / "canon" / "Entity-relationship-matrix.md").exists()


def test_execute_deletes_world_readme(tmp_path):
    """canon/world/README.md should be deleted after migration."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    assert not (tmp_path / "canon" / "world" / "README.md").exists()


def test_execute_updates_skill_refs(tmp_path):
    """Skills should no longer reference bible/."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    for skill_dir in (tmp_path / ".claude" / "skills").iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert "bible/" not in content, f"Stale bible/ ref in {skill_file}"


def test_execute_updates_claude_md(tmp_path):
    """CLAUDE.md should no longer reference bible/."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    content = (tmp_path / "CLAUDE.md").read_text()
    assert "bible/" not in content.lower()


def test_execute_creates_rollback_manifest(tmp_path):
    """--execute should create a rollback manifest file."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    assert (tmp_path / ".migration-rollback.yaml").exists()


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------


def test_rollback_reverts(tmp_path):
    """--rollback should restore bible/ from rollback file."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    assert not (tmp_path / "bible" / "story-bible.md").exists()
    run_migration(tmp_path, rollback=True)
    assert (tmp_path / "bible" / "story-bible.md").exists()
    assert (tmp_path / "bible" / "world-rules.md").exists()


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------


def test_verify_passes_after_execute(tmp_path):
    """--verify should pass after a clean migration."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    result = run_migration(tmp_path, verify=True)
    assert result.ok, f"Verify failed: {result.report}"


def test_verify_catches_broken_refs(tmp_path):
    """--verify should fail if skills still reference bible/."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    # Manually break a ref
    skill = tmp_path / ".claude" / "skills" / "continuity-callback" / "SKILL.md"
    skill.write_text(skill.read_text().replace("canon", "bible"))
    result = run_migration(tmp_path, verify=True)
    assert not result.ok


def test_verify_scans_entire_repo(tmp_path):
    """--verify should catch bible/ refs in docs too."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    # Plant a stale ref in docs/
    stale_doc = tmp_path / "docs" / "some_doc.md"
    stale_doc.write_text("See bible/story-bible.md for details.")
    result = run_migration(tmp_path, verify=True)
    assert not result.ok
    report = result.report
    assert any("docs" in str(ref.get("file", "")) for ref in report.get("remaining_refs", []))


def test_verify_produces_report_with_counts(tmp_path):
    """--verify should produce a report with files_scanned and remaining_refs."""
    create_test_repo(tmp_path)
    run_migration(tmp_path, execute=True)
    result = run_migration(tmp_path, verify=True)
    assert "files_scanned" in result.report
    assert "remaining_refs" in result.report
