#!/usr/bin/env python3
"""Validate AI co-author project setup.

Checks canonical structure, style-sample minimums, and preferences file presence.
Exits non-zero with actionable messages when requirements are not met.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass
class CheckResult:
    ok: bool
    message: str


def check_exists(path: Path, label: str) -> CheckResult:
    if path.exists():
        return CheckResult(True, f"PASS: {label} exists ({path})")
    return CheckResult(False, f"FAIL: {label} missing ({path})")


def count_markdown_files(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for p in path.iterdir() if p.is_file() and p.suffix.lower() == ".md")


def run_checks(root: Path, min_style_samples: int) -> list[CheckResult]:
    canon = root / "canon"
    results = [
        check_exists(canon / "index.md", "Canon index"),
        check_exists(canon / "timeline.md", "Canon timeline"),
        check_exists(canon / "preferences.md", "Preference log"),
        check_exists(canon / "characters", "Character directory"),
        check_exists(canon / "world", "World directory"),
        check_exists(canon / "tech", "Tech directory"),
        check_exists(canon / "themes", "Theme directory"),
        check_exists(canon / "style-samples", "Style samples directory"),
    ]

    sample_dir = canon / "style-samples"
    sample_count = count_markdown_files(sample_dir)
    if sample_count >= min_style_samples:
        results.append(
            CheckResult(
                True,
                f"PASS: style sample count is {sample_count} (minimum {min_style_samples})",
            )
        )
    else:
        results.append(
            CheckResult(
                False,
                f"FAIL: style sample count is {sample_count}; need at least {min_style_samples} markdown files in {sample_dir}",
            )
        )

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AI co-author setup")
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--min-style-samples",
        type=int,
        default=3,
        help="Minimum required number of style sample markdown files (default: 3)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    checks = run_checks(root, args.min_style_samples)

    failures = 0
    for result in checks:
        print(result.message)
        if not result.ok:
            failures += 1

    if failures:
        print(f"\nValidation failed with {failures} issue(s).")
        return 1

    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
