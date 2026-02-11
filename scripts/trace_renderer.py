"""Render a trace JSON file into a human-readable Markdown file.

Usage:
    python scripts/trace_renderer.py <trace.json> [--output <trace.md>]

If --output is not specified, writes to the same path with .md extension.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def render(trace: dict) -> str:
    """Convert a trace_record dict into rendered Markdown."""
    lines: list[str] = []

    step = trace.get("step", "unknown")
    level = trace.get("level", "?")
    mode = trace.get("mode", "manual")
    timestamp = trace.get("timestamp", "")

    # --- Header ---
    lines.append(f"# Trace: {step} — {mode}")
    lines.append("")
    model_cfg = trace.get("model_config", {})
    model_summary = ", ".join(f"{k}: {v}" for k, v in model_cfg.items()) if model_cfg else "n/a"
    lines.append(f"**Timestamp**: {timestamp}")
    lines.append(f"**Step**: {step} | **Level**: {level} | **Mode**: {mode}")
    lines.append(f"**Model config**: {model_summary}")
    lines.append("")

    # --- Context Loaded ---
    lines.append("## Context Loaded")
    context = trace.get("context_loaded", [])
    if context:
        for entry in context:
            f = entry.get("file", "?")
            tokens = entry.get("tokens")
            tok_str = f" ({tokens:,} tokens)" if tokens else ""
            lines.append(f"- `{f}`{tok_str}")
    else:
        lines.append("- (none)")
    lines.append("")

    # --- Phase 1: Structure ---
    phases = trace.get("phases", {})
    structure = phases.get("structure", {})
    lines.append("## Phase 1: Structure")
    lines.append(f"**Human input**: {structure.get('human_input', 'n/a')}")
    lines.append(f"**Lead Editor output**: {structure.get('lead_editor_output', 'n/a')}")
    accepted = structure.get("human_accepted")
    acc_str = "yes" if accepted else ("no" if accepted is False else "n/a")
    adjustments = structure.get("adjustments", "")
    lines.append(f"**Human accepted**: {acc_str} | **Adjustments**: {adjustments or 'none'}")
    lines.append("")

    # --- Phase 2: Comments ---
    lines.append("## Phase 2: Comments")
    lines.append("")
    comments = phases.get("comments", [])
    if not comments:
        lines.append("(no comments)")
    for c in comments:
        agent = c.get("agent", "unknown")
        model = c.get("model", "?")
        lines.append(f"### {agent} ({model})")
        lines.append(f"**Comment**: {c.get('comment', '')}")
        cites = c.get("citations", [])
        lines.append(f"**Citations**: {', '.join(f'`{x}`' for x in cites) if cites else 'none'}")
        lines.append(f"**Citation Status**: {c.get('citation_status', 'unknown')}")
        resolution = c.get("resolution", "pending")
        lines.append(f"**Resolution**: {resolution or 'pending'}")
        lines.append(f"<!-- HUMAN-EVAL: comment-quality=___/5, relevance=___/5 -->")
        lines.append("")

    # --- Artifact Committed ---
    commit = phases.get("commit", {})
    lines.append("## Artifact Committed")
    lines.append(f"**File**: {commit.get('artifact_file', 'n/a')}")
    r_added = commit.get("relationships_added", 0)
    r_changed = commit.get("relationships_changed", 0)
    lines.append(f"**Relationships updated**: {r_added} new, {r_changed} changed")
    lines.append("")

    # --- Cost ---
    cost = trace.get("cost", {})
    lines.append("## Cost")
    lines.append("| Agent | Model | Input tokens | Output tokens | Cost |")
    lines.append("|-------|-------|-------------|--------------|------|")
    by_agent = cost.get("by_agent", {})
    for agent_name, info in by_agent.items():
        m = info.get("model", "?")
        inp = info.get("input_tokens", 0)
        out = info.get("output_tokens", 0)
        c = info.get("cost_usd", 0.0)
        lines.append(f"| {agent_name} | {m} | {inp:,} | {out:,} | ${c:.4f} |")
    total = cost.get("total_usd", 0.0)
    lines.append(f"| **Total** | | | | **${total:.4f}** |")
    lines.append("")

    # --- Reproducibility ---
    repro = trace.get("reproducibility", {})
    lines.append("## Reproducibility")
    lines.append(f"**Context manifest hash**: {repro.get('context_manifest_hash', 'n/a')}")
    lines.append(f"**Canon version**: {repro.get('canon_version', 'n/a')}")
    lines.append("")

    return "\n".join(lines)


def render_file(json_path: Path, output_path: Path | None = None) -> Path:
    """Read a trace JSON file, render to Markdown, and write the output."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    md = render(data)
    if output_path is None:
        output_path = json_path.with_suffix(".md")
    output_path.write_text(md, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render trace JSON to Markdown.")
    parser.add_argument("json_path", type=Path, help="Path to trace .json file")
    parser.add_argument("--output", type=Path, default=None, help="Output .md path")
    args = parser.parse_args()

    if not args.json_path.exists():
        print(f"ERROR: {args.json_path} not found", file=sys.stderr)
        sys.exit(1)

    out = render_file(args.json_path, args.output)
    print(f"Rendered: {out}")


if __name__ == "__main__":
    main()
