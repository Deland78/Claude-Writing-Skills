"""Shared pytest fixtures for the fiction-pipeline test suite."""

from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the project root."""
    return PROJECT_ROOT


@pytest.fixture
def canon_fixture_tree(tmp_path: Path) -> Path:
    """Build a fully-populated mock canon tree for context loader tests.

    Returns the root of the temporary project directory.
    All files contain minimal stub content with correct paths.
    """
    # Root files
    (tmp_path / "CLAUDE.md").write_text("# Project Guide\nStub CLAUDE.md for testing.\n")
    (tmp_path / ".pipeline-state.yaml").write_text(
        "position:\n  level: L1\n  act: null\n  chapter: null\n  scene: null\n"
        "mode: manual\n"
        "canon_version: 1\n"
        "max_context_tokens: 100000\n"
    )

    # canon/
    canon = tmp_path / "canon"
    canon.mkdir()
    (canon / "index.md").write_text(
        "# Canon Index\n\n## Modules\n- timeline.md\n- preferences.md\n"
        "- characters/\n- world/\n- acts/\n- relationships.yaml\n- style-samples/\n"
    )
    (canon / "story-concept.md").write_text("# Story Concept\nStub L1 output.\n")
    (canon / "story-arc.md").write_text("# Story Arc\nStub L2 output.\n")
    (canon / "timeline.md").write_text("# Canon Timeline\nStub timeline.\n")
    (canon / "preferences.md").write_text("# Preferences\nStub preferences.\n")
    (canon / "relationships.yaml").write_text(
        "rel_vocabulary:\n  positive: [trusts, loves]\n  negative: [distrusts, fears]\n"
        "  neutral: [knows]\n  causal: [caused]\n\n"
        "entities: {}\n\nrelationships: []\n"
    )

    # canon/characters/
    chars = canon / "characters"
    chars.mkdir()
    (chars / "marcus.md").write_text("# Marcus\nStub character profile.\n")

    # canon/world/
    world = canon / "world"
    world.mkdir()
    (world / "story-bible.md").write_text("# Story Bible\nStub story bible.\n")
    (world / "world-rules.md").write_text("# World Rules\nStub world rules.\n")

    # canon/acts/
    acts = canon / "acts"
    acts.mkdir()
    (acts / "act-1-outline.md").write_text("# Act 1 Outline\nStub L3 output.\n")
    (acts / "act-2-outline.md").write_text("# Act 2 Outline\nStub L3 output.\n")

    # canon/acts/act-1/
    act1 = acts / "act-1"
    act1.mkdir()
    (act1 / "ch1-outline.md").write_text("# Chapter 1 Outline\nStub L4 output.\n")
    (act1 / "ch2-outline.md").write_text("# Chapter 2 Outline\nStub L4 output.\n")

    # canon/acts/act-1/ch1/
    ch1 = act1 / "ch1"
    ch1.mkdir()
    (ch1 / "sc1-draft.md").write_text("# Scene 1 Draft\nStub L5 output.\n")

    # canon/style-samples/
    samples = canon / "style-samples"
    samples.mkdir()
    (samples / "sample-01.md").write_text("# Style Sample 1\nStub sample.\n")

    return tmp_path
