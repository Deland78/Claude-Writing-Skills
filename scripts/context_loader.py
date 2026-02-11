#!/usr/bin/env python3
"""Context loader for the fiction writing pipeline.

Reads .pipeline-state.yaml and generates a deterministic context manifest
based on the current position in the story hierarchy.

Usage:
    python scripts/context_loader.py --state .pipeline-state.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml


# Approximate tokens per byte (conservative estimate for English markdown).
_TOKENS_PER_BYTE = 0.25


# ---------------------------------------------------------------------------
# State loading
# ---------------------------------------------------------------------------

def load_state(state_path: Path) -> dict[str, Any]:
    """Load the pipeline state YAML file."""
    with open(state_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Manifest generation rules
# ---------------------------------------------------------------------------

# System files always loaded regardless of level.
_SYSTEM_FILES = [
    "CLAUDE.md",
    "canon/index.md",
    "canon/preferences.md",
    "canon/relationships.yaml",
]


def get_manifest(state: dict[str, Any], root: Path) -> list[str]:
    """Generate the context file manifest based on pipeline state.

    Rules:
        L1 (concept): system files only
        L2 (arc):     system + story-concept
        L3 (act):     system + concept + arc + sibling act outlines + current act outline
        L4 (chapter): system + concept + arc + act outline + sibling ch outlines + current ch outline + characters
        L5 (scene):   system + concept + arc + act outline + ch outline + characters
    """
    level = state.get("position", {}).get("level", "L1")
    act = state.get("position", {}).get("act")
    chapter = state.get("position", {}).get("chapter")

    files: list[str] = []

    # Always include system files that exist.
    for sf in _SYSTEM_FILES:
        if (root / sf).exists():
            files.append(sf)

    if level == "L1":
        return files

    # L2+: add story concept
    _add_if_exists(files, root, "canon/story-concept.md")

    if level == "L2":
        return files

    # L3+: add story arc + act outlines
    _add_if_exists(files, root, "canon/story-arc.md")

    if level in ("L3", "L4", "L5") and act is not None:
        # Add all sibling act outlines (for cross-act awareness)
        acts_dir = root / "canon" / "acts"
        if acts_dir.exists():
            for outline in sorted(acts_dir.glob("act-*-outline.md")):
                rel = f"canon/acts/{outline.name}"
                if rel not in files:
                    files.append(rel)

    if level == "L3":
        return files

    # L4+: add current act's chapter outlines + character files
    if act is not None:
        act_dir = root / "canon" / "acts" / f"act-{act}"
        if act_dir.exists():
            for ch_outline in sorted(act_dir.glob("ch*-outline.md")):
                rel = f"canon/acts/act-{act}/{ch_outline.name}"
                if rel not in files:
                    files.append(rel)

    # Add character files
    chars_dir = root / "canon" / "characters"
    if chars_dir.exists():
        for char_file in sorted(chars_dir.glob("*.md")):
            if char_file.name == "README.md":
                continue
            rel = f"canon/characters/{char_file.name}"
            if rel not in files:
                files.append(rel)

    if level == "L4":
        return files

    # L5: add chapter outline (already added above) — no scene siblings to avoid context bloat.
    return files


def _add_if_exists(files: list[str], root: Path, rel_path: str) -> None:
    """Append rel_path to files if the file exists on disk."""
    if (root / rel_path).exists() and rel_path not in files:
        files.append(rel_path)


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def estimate_tokens(root: Path, files: list[str]) -> int:
    """Estimate total tokens for a set of files based on byte count."""
    total_bytes = 0
    for f in files:
        fpath = root / f
        if fpath.exists():
            try:
                total_bytes += fpath.stat().st_size
            except OSError:
                pass
    return int(total_bytes * _TOKENS_PER_BYTE)


# ---------------------------------------------------------------------------
# Manifest with metadata
# ---------------------------------------------------------------------------

def get_manifest_with_meta(state: dict[str, Any], root: Path) -> dict[str, Any]:
    """Return the manifest plus metadata (token estimate, hash)."""
    files = get_manifest(state, root)
    return {
        "files": files,
        "total_estimated_tokens": estimate_tokens(root, files),
        "manifest_hash": get_manifest_hash(state, root),
    }


def get_manifest_hash(state: dict[str, Any], root: Path) -> str:
    """Compute a deterministic hash of the manifest for reproducibility."""
    files = get_manifest(state, root)
    content = json.dumps(files, sort_keys=False)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def get_reproducibility_bundle(state: dict[str, Any], root: Path) -> dict[str, Any]:
    """Build the reproducibility bundle for trace records."""
    return {
        "context_manifest_hash": get_manifest_hash(state, root),
        "canon_version": state.get("canon_version", 0),
        "agent_config": state.get("agents", {}),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate context manifest from pipeline state")
    parser.add_argument("--state", required=True, help="Path to .pipeline-state.yaml")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args(argv)

    state_path = Path(args.state)
    root = Path(args.root).resolve()

    if not state_path.exists():
        print(f"State file not found: {state_path}", file=sys.stderr)
        return 1

    state = load_state(state_path)
    meta = get_manifest_with_meta(state, root)

    print("Context manifest:")
    for f in meta["files"]:
        exists = "OK" if (root / f).exists() else "MISSING"
        print(f"  [{exists}] {f}")
    print(f"\nTotal files: {len(meta['files'])}")
    print(f"Estimated tokens: {meta['total_estimated_tokens']}")
    print(f"Manifest hash: {meta['manifest_hash']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
