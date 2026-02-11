"""Tests for the trace renderer (P2A.2).

Verifies that trace_renderer.py correctly converts JSON trace records
into human-readable Markdown. Does NOT test trace generation.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from trace_renderer import render, render_file

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_TRACE = {
    "timestamp": "2026-02-10T16:30:00Z",
    "step": "L2/Arc",
    "level": "L2",
    "mode": "mob",
    "context_loaded": [],
    "cost": {"total_usd": 0.0},
}

FULL_TRACE = {
    "timestamp": "2026-02-10T16:30:00Z",
    "step": "L2/Arc",
    "level": "L2",
    "mode": "mob",
    "model_config": {
        "lead_editor": "claude-haiku",
        "plot_analyst": "claude-haiku",
    },
    "context_loaded": [
        {"file": "canon/story-concept.md", "tokens": 1204},
        {"file": "canon/story-arc.md", "tokens": 2891},
    ],
    "phases": {
        "structure": {
            "human_input": "Raw concept notes",
            "lead_editor_output": "Structured concept",
            "human_accepted": True,
            "adjustments": "",
        },
        "comments": [
            {
                "agent": "plot_analyst",
                "model": "claude-haiku",
                "comment": "Act 2A lacks a pinch point.",
                "citations": ["canon/story-arc.md#L45"],
                "citation_status": "cited",
                "suggested_changes": [],
                "resolution": "accepted",
            },
            {
                "agent": "depth_partner",
                "model": "claude-haiku",
                "comment": "Theme is underdeveloped in Act 1.",
                "citations": [],
                "citation_status": "advisory",
                "suggested_changes": [],
                "resolution": "deferred",
            },
        ],
        "commit": {
            "artifact_file": "canon/story-arc.md",
            "relationships_added": 2,
            "relationships_changed": 0,
            "canon_version": 5,
        },
    },
    "cost": {
        "total_usd": 0.008,
        "by_agent": {
            "plot_analyst": {
                "model": "claude-haiku",
                "input_tokens": 6500,
                "output_tokens": 450,
                "cost_usd": 0.004,
            },
            "depth_partner": {
                "model": "claude-haiku",
                "input_tokens": 6500,
                "output_tokens": 300,
                "cost_usd": 0.004,
            },
        },
    },
    "reproducibility": {
        "context_manifest_hash": "sha256:abc123",
        "canon_version": 5,
    },
}


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


def test_minimal_trace_renders_without_error():
    """A minimal trace with only required fields should render."""
    md = render(MINIMAL_TRACE)
    assert isinstance(md, str)
    assert len(md) > 0


def test_full_trace_has_required_headings():
    """Rendered markdown must contain all required section headings."""
    md = render(FULL_TRACE)
    required = [
        "## Context Loaded",
        "## Phase 1: Structure",
        "## Phase 2: Comments",
        "## Artifact Committed",
        "## Cost",
        "## Reproducibility",
    ]
    for heading in required:
        assert heading in md, f"Missing heading: {heading}"


def test_full_trace_contains_agent_comments():
    """Agent comments should appear in rendered output with correct labels."""
    md = render(FULL_TRACE)
    assert "plot_analyst" in md
    assert "depth_partner" in md
    assert "Act 2A lacks a pinch point" in md
    assert "cited" in md
    assert "advisory" in md


def test_full_trace_contains_resolution():
    """Each comment should show its resolution status."""
    md = render(FULL_TRACE)
    assert "accepted" in md
    assert "deferred" in md


def test_full_trace_contains_cost_table():
    """Rendered markdown should include a cost table with agent rows."""
    md = render(FULL_TRACE)
    assert "| plot_analyst" in md
    assert "| depth_partner" in md
    assert "**Total**" in md


def test_full_trace_contains_reproducibility():
    """Rendered markdown should include reproducibility bundle."""
    md = render(FULL_TRACE)
    assert "sha256:abc123" in md
    assert "5" in md  # canon_version


def test_full_trace_contains_human_eval_placeholder():
    """Each comment should have a HUMAN-EVAL placeholder for optional annotation."""
    md = render(FULL_TRACE)
    eval_count = md.count("<!-- HUMAN-EVAL:")
    assert eval_count == 2, f"Expected 2 HUMAN-EVAL placeholders, got {eval_count}"


def test_context_loaded_lists_files():
    """Context loaded section should list files with token counts."""
    md = render(FULL_TRACE)
    assert "canon/story-concept.md" in md
    assert "1,204 tokens" in md


def test_render_file_writes_output(tmp_path):
    """render_file should write markdown to disk."""
    json_path = tmp_path / "test.trace.json"
    json_path.write_text(json.dumps(FULL_TRACE), encoding="utf-8")

    out = render_file(json_path)
    assert out.exists()
    assert out.suffix == ".md"
    content = out.read_text(encoding="utf-8")
    assert "## Phase 2: Comments" in content


def test_render_file_custom_output(tmp_path):
    """render_file with explicit output path should write to that path."""
    json_path = tmp_path / "test.trace.json"
    json_path.write_text(json.dumps(FULL_TRACE), encoding="utf-8")
    custom_out = tmp_path / "custom.md"

    out = render_file(json_path, custom_out)
    assert out == custom_out
    assert custom_out.exists()


# ---------------------------------------------------------------------------
# Template existence
# ---------------------------------------------------------------------------


def test_trace_template_exists():
    """The trace template must exist in templates/."""
    assert (TEMPLATES_DIR / "trace.template.md").exists()
