"""TDD tests for the context loader.

Tests the manifest generation rules at each pipeline level (L1-L5).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from context_loader import (
    get_manifest,
    get_manifest_hash,
    get_manifest_with_meta,
    get_reproducibility_bundle,
)


def make_state(
    level: str = "L1",
    act: int | None = None,
    chapter: int | None = None,
    scene: int | None = None,
) -> dict:
    """Helper to build a pipeline state dict."""
    return {
        "position": {
            "level": level,
            "act": act,
            "chapter": chapter,
            "scene": scene,
        },
        "mode": "manual",
        "canon_version": 1,
        "max_context_tokens": 100000,
        "agents": {
            "lead_editor": {"model": "claude-haiku", "active": True},
        },
    }


# ---------------------------------------------------------------------------
# L1 — Concept
# ---------------------------------------------------------------------------


def test_l1_concept_loads_system_files_only(canon_fixture_tree):
    """At L1 (story concept), only system files should be loaded."""
    state = make_state(level="L1")
    files = get_manifest(state, root=canon_fixture_tree)
    assert "CLAUDE.md" in files
    assert "canon/index.md" in files
    assert "canon/preferences.md" in files
    assert "canon/relationships.yaml" in files
    assert not any("acts/" in f for f in files)
    assert not any("story-concept" in f for f in files)


# ---------------------------------------------------------------------------
# L2 — Arc
# ---------------------------------------------------------------------------


def test_l2_loads_system_plus_concept(canon_fixture_tree):
    """At L2, should load system files + story-concept.md."""
    state = make_state(level="L2")
    files = get_manifest(state, root=canon_fixture_tree)
    assert "CLAUDE.md" in files
    assert "canon/story-concept.md" in files
    assert not any("acts/" in f for f in files)
    assert not any("story-arc" in f for f in files)


# ---------------------------------------------------------------------------
# L3 — Act
# ---------------------------------------------------------------------------


def test_l3_act2_loads_parent_chain_plus_sibling(canon_fixture_tree):
    """At L3/Act2, should load: concept, arc, act-1-outline (sibling), act-2-outline."""
    state = make_state(level="L3", act=2)
    files = get_manifest(state, root=canon_fixture_tree)
    assert "canon/story-concept.md" in files
    assert "canon/story-arc.md" in files
    assert "canon/acts/act-1-outline.md" in files  # sibling
    assert "canon/acts/act-2-outline.md" in files  # current


def test_l3_does_not_load_chapter_outlines(canon_fixture_tree):
    """At L3, chapter outlines should NOT be loaded."""
    state = make_state(level="L3", act=1)
    files = get_manifest(state, root=canon_fixture_tree)
    assert not any("ch1-outline" in f for f in files)
    assert not any("ch2-outline" in f for f in files)


# ---------------------------------------------------------------------------
# L4 — Chapter
# ---------------------------------------------------------------------------


def test_l4_loads_chapter_outlines_and_characters(canon_fixture_tree):
    """At L4, should load act's chapter outlines + character files."""
    state = make_state(level="L4", act=1, chapter=1)
    files = get_manifest(state, root=canon_fixture_tree)
    assert "canon/story-concept.md" in files
    assert "canon/story-arc.md" in files
    assert "canon/acts/act-1-outline.md" in files
    assert "canon/acts/act-1/ch1-outline.md" in files
    assert "canon/acts/act-1/ch2-outline.md" in files
    assert "canon/characters/marcus.md" in files


def test_l4_does_not_load_scene_drafts(canon_fixture_tree):
    """At L4, scene drafts should NOT be loaded."""
    state = make_state(level="L4", act=1, chapter=1)
    files = get_manifest(state, root=canon_fixture_tree)
    assert not any("sc1-draft" in f for f in files)


# ---------------------------------------------------------------------------
# L5 — Scene
# ---------------------------------------------------------------------------


def test_l5_scene_loads_chapter_outline_and_characters(canon_fixture_tree):
    """At L5, should load chapter outline + characters."""
    state = make_state(level="L5", act=1, chapter=2, scene=1)
    files = get_manifest(state, root=canon_fixture_tree)
    assert "canon/acts/act-1/ch2-outline.md" in files
    assert "canon/characters/marcus.md" in files


def test_l5_does_not_load_sibling_scenes(canon_fixture_tree):
    """At L5, should NOT load scene drafts from other scenes."""
    state = make_state(level="L5", act=1, chapter=1, scene=1)
    files = get_manifest(state, root=canon_fixture_tree)
    # The manifest should NOT include scene draft files
    assert not any("sc1-draft" in f for f in files)


# ---------------------------------------------------------------------------
# Manifest metadata
# ---------------------------------------------------------------------------


def test_manifest_hash_is_deterministic(canon_fixture_tree):
    """Same state should produce same manifest hash."""
    state = make_state(level="L3", act=1)
    hash1 = get_manifest_hash(state, root=canon_fixture_tree)
    hash2 = get_manifest_hash(state, root=canon_fixture_tree)
    assert hash1 == hash2
    assert len(hash1) == 16  # truncated sha256


def test_manifest_includes_token_estimate(canon_fixture_tree):
    """Manifest output should include total_estimated_tokens field."""
    state = make_state(level="L3", act=1)
    manifest = get_manifest_with_meta(state, root=canon_fixture_tree)
    assert "total_estimated_tokens" in manifest
    assert isinstance(manifest["total_estimated_tokens"], int)
    assert manifest["total_estimated_tokens"] > 0


def test_reproducibility_bundle_includes_all_fields(canon_fixture_tree):
    """Reproducibility bundle should have manifest_hash, canon_version, agent_config."""
    state = make_state(level="L3", act=1)
    bundle = get_reproducibility_bundle(state, root=canon_fixture_tree)
    assert "context_manifest_hash" in bundle
    assert "canon_version" in bundle
    assert "agent_config" in bundle
    assert bundle["canon_version"] == 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_manifest_handles_missing_files_gracefully(canon_fixture_tree):
    """If a canonical file doesn't exist yet, it should be omitted, not crash."""
    state = make_state(level="L3", act=3)  # act-3 doesn't exist in fixture
    files = get_manifest(state, root=canon_fixture_tree)
    assert "canon/acts/act-3-outline.md" not in files
    # Should still include parent chain that does exist
    assert "canon/story-concept.md" in files
    assert "canon/story-arc.md" in files


def test_manifest_no_duplicates(canon_fixture_tree):
    """Manifest should never contain duplicate file paths."""
    state = make_state(level="L5", act=1, chapter=1, scene=1)
    files = get_manifest(state, root=canon_fixture_tree)
    assert len(files) == len(set(files))


def test_different_levels_produce_different_hashes(canon_fixture_tree):
    """Different pipeline levels should produce different manifest hashes."""
    state_l1 = make_state(level="L1")
    state_l3 = make_state(level="L3", act=1)
    hash1 = get_manifest_hash(state_l1, root=canon_fixture_tree)
    hash3 = get_manifest_hash(state_l3, root=canon_fixture_tree)
    assert hash1 != hash3
