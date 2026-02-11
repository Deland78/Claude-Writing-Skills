#!/usr/bin/env python3
"""Migration script: move bible/ files to canon/ with reference updates.

Standalone Python 3.11+ script using only stdlib (with optional PyYAML).
Provides dry-run, execute (atomic with rollback manifest), rollback, and
full-repo verify modes.
"""
from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Optional YAML support – fall back to a simple emitter/loader
# ---------------------------------------------------------------------------
try:
    import yaml as _yaml  # type: ignore[import-untyped]

    def _dump_yaml(data: Any) -> str:
        return _yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def _load_yaml(text: str) -> Any:
        return _yaml.safe_load(text)

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

    def _dump_yaml(data: Any) -> str:  # type: ignore[misc]
        """Minimal YAML-like serialiser (supports dict, list, str, bool, int, None)."""
        buf = io.StringIO()
        _simple_yaml_write(buf, data, indent=0)
        return buf.getvalue()

    def _load_yaml(text: str) -> Any:  # type: ignore[misc]
        """Minimal YAML-like loader (supports the subset we emit)."""
        return _simple_yaml_read(text)


# ---- simple YAML helpers (fallback) --------------------------------------

def _simple_yaml_write(buf: io.StringIO, obj: Any, indent: int) -> None:
    prefix = "  " * indent
    if obj is None:
        buf.write("null\n")
    elif isinstance(obj, bool):
        buf.write("true\n" if obj else "false\n")
    elif isinstance(obj, int):
        buf.write(f"{obj}\n")
    elif isinstance(obj, str):
        if "\n" in obj:
            buf.write("|\n")
            for line in obj.splitlines(keepends=True):
                buf.write(f"{prefix}  {line}")
            if not obj.endswith("\n"):
                buf.write("\n")
        else:
            # Quote if the string could be confused with YAML specials
            safe = obj.replace("\\", "\\\\").replace('"', '\\"')
            buf.write(f'"{safe}"\n')
    elif isinstance(obj, list):
        if not obj:
            buf.write("[]\n")
            return
        buf.write("\n")
        for item in obj:
            buf.write(f"{prefix}- ")
            _simple_yaml_write(buf, item, indent + 1)
    elif isinstance(obj, dict):
        if not obj:
            buf.write("{}\n")
            return
        buf.write("\n")
        for key, val in obj.items():
            buf.write(f"{prefix}{key}: ")
            _simple_yaml_write(buf, val, indent + 1)
    else:
        buf.write(f'"{obj!s}"\n')


def _simple_yaml_read(text: str) -> Any:
    """Parse a very restricted YAML subset back into Python objects.

    This only needs to handle the structure we emit ourselves (nested dicts,
    lists, strings with literal-block scalars, booleans, ints, and null).
    """
    lines = text.splitlines()
    result, _ = _parse_yaml_value(lines, 0, 0)
    return result


def _yaml_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_yaml_value(lines: list[str], idx: int, base_indent: int) -> tuple[Any, int]:
    """Return (parsed_value, next_line_index)."""
    if idx >= len(lines):
        return None, idx

    line = lines[idx]
    stripped = line.strip()

    # Skip blank / comment lines
    while idx < len(lines) and (not lines[idx].strip() or lines[idx].strip().startswith("#")):
        idx += 1
        if idx >= len(lines):
            return None, idx
        line = lines[idx]
        stripped = line.strip()

    # Detect list
    if stripped.startswith("- "):
        return _parse_yaml_list(lines, idx, _yaml_indent(line))

    # Detect mapping key
    if ":" in stripped and not stripped.startswith("|"):
        return _parse_yaml_mapping(lines, idx, _yaml_indent(line))

    # Scalar
    return _parse_scalar(stripped), idx + 1


def _parse_scalar(s: str) -> Any:
    s = s.strip()
    if s in ("null", "~", ""):
        return None
    if s == "true":
        return True
    if s == "false":
        return False
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s == "[]":
        return []
    if s == "{}":
        return {}
    try:
        return int(s)
    except ValueError:
        return s


def _parse_yaml_mapping(lines: list[str], idx: int, base_indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while idx < len(lines):
        line = lines[idx]
        if not line.strip() or line.strip().startswith("#"):
            idx += 1
            continue
        ind = _yaml_indent(line)
        if ind < base_indent:
            break
        if ind > base_indent:
            break
        stripped = line.strip()
        if stripped.startswith("- "):
            break
        colon_pos = stripped.find(":")
        if colon_pos == -1:
            break
        key = stripped[:colon_pos].strip()
        rest = stripped[colon_pos + 1 :].strip()
        if rest == "|":
            # Literal block scalar
            idx += 1
            block_lines: list[str] = []
            block_indent: int | None = None
            while idx < len(lines):
                bl = lines[idx]
                if not bl.strip():
                    block_lines.append("")
                    idx += 1
                    continue
                bi = _yaml_indent(bl)
                if block_indent is None:
                    block_indent = bi
                if bi < (block_indent or base_indent + 2):
                    break
                block_lines.append(bl[block_indent:] if block_indent else bl.lstrip())
                idx += 1
            result[key] = "\n".join(block_lines)
            if result[key] and not result[key].endswith("\n"):
                result[key] += "\n"
        elif rest == "" or rest is None:
            # Value on next line(s) – could be mapping or list
            idx += 1
            if idx < len(lines):
                next_line = lines[idx]
                if next_line.strip():
                    ni = _yaml_indent(next_line)
                    if ni > base_indent:
                        val, idx = _parse_yaml_value(lines, idx, ni)
                        result[key] = val
                    else:
                        result[key] = None
                else:
                    result[key] = None
            else:
                result[key] = None
        else:
            result[key] = _parse_scalar(rest)
            idx += 1
    return result, idx


def _parse_yaml_list(lines: list[str], idx: int, base_indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while idx < len(lines):
        line = lines[idx]
        if not line.strip() or line.strip().startswith("#"):
            idx += 1
            continue
        ind = _yaml_indent(line)
        if ind < base_indent:
            break
        stripped = line.strip()
        if not stripped.startswith("- "):
            break
        item_text = stripped[2:].strip()
        if ":" in item_text and not item_text.startswith('"'):
            # Inline mapping item or multi-line mapping item
            # Re-parse as mapping starting from this line with increased indent
            # Build a synthetic set of lines for the mapping
            colon_pos = item_text.find(":")
            key = item_text[:colon_pos].strip()
            rest = item_text[colon_pos + 1 :].strip()
            if rest:
                result.append({key: _parse_scalar(rest)})
                idx += 1
            else:
                # Multi-key mapping as list item
                mapping: dict[str, Any] = {}
                # First key
                mapping[key] = None
                idx += 1
                item_indent = ind + 2
                while idx < len(lines):
                    cl = lines[idx]
                    if not cl.strip():
                        idx += 1
                        continue
                    ci = _yaml_indent(cl)
                    if ci < item_indent:
                        break
                    cs = cl.strip()
                    cp = cs.find(":")
                    if cp == -1:
                        break
                    ck = cs[:cp].strip()
                    cr = cs[cp + 1 :].strip()
                    mapping[ck] = _parse_scalar(cr) if cr else None
                    idx += 1
                result.append(mapping)
        else:
            result.append(_parse_scalar(item_text))
            idx += 1
    return result, idx


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class MigrationError(Exception):
    """Raised when the migration encounters an unrecoverable error."""


# ---------------------------------------------------------------------------
# Result container for --verify
# ---------------------------------------------------------------------------

@dataclass
class MigrationResult:
    ok: bool
    report: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Reference replacement rules
# ---------------------------------------------------------------------------

# Ordered list of (pattern, replacement) applied to file content.
# More specific patterns MUST come before generic ones.
REF_REPLACEMENTS: list[tuple[str, str]] = [
    # Specific file-path references
    ("bible/story-bible.md", "canon/world/story-bible.md"),
    ("bible/world-rules.md", "canon/world/world-rules.md"),
    ("bible/scene-tracker.md", "canon/timeline.md"),
    # Parameter-name renames
    ("book_bible_or_notes", "canon_reference_docs"),
    ("character_bible", "character_profiles"),
    # Generic bible/ prefix (must be last)
    ("bible/", "canon/"),
]

# We also handle a case-preserving variant for prose references like
# "Bible, World Rules" in CLAUDE.md descriptions.  The generic rule
# above already covers path-like references; we add a special rule
# for the directory listing line that names the directory.
_BIBLE_DIR_DESCRIPTION = re.compile(
    r"`bible/`:\s*Active story reference documents \(Bible, World Rules, Scene Tracker\)\.",
    re.IGNORECASE,
)
_BIBLE_DIR_REPLACEMENT = (
    "`canon/`: Active story reference documents (Story Bible, World Rules, Timeline)."
)


# ---------------------------------------------------------------------------
# File-move mapping
# ---------------------------------------------------------------------------

@dataclass
class _MoveOp:
    """Describes a file operation."""
    src: Path        # relative to root
    dst: Path | None  # None → delete
    merge: bool = False  # True → append src content to existing dst


def _build_ops() -> list[_MoveOp]:
    """Return the ordered list of file operations."""
    return [
        _MoveOp(
            src=Path("bible/story-bible.md"),
            dst=Path("canon/world/story-bible.md"),
        ),
        _MoveOp(
            src=Path("bible/world-rules.md"),
            dst=Path("canon/world/world-rules.md"),
        ),
        _MoveOp(
            src=Path("bible/scene-tracker.md"),
            dst=Path("canon/timeline.md"),
            merge=True,
        ),
        _MoveOp(
            src=Path("canon/Entity-relationship-matrix.md"),
            dst=None,  # delete
        ),
        _MoveOp(
            src=Path("canon/world/README.md"),
            dst=None,  # delete after story-bible.md is in place
        ),
    ]


# ---------------------------------------------------------------------------
# Files whose content gets reference-updated
# ---------------------------------------------------------------------------

def _ref_update_globs() -> list[str]:
    """Return glob patterns for files whose *content* should be ref-updated."""
    return [
        ".claude/skills/*/*.md",
        "CLAUDE.md",
    ]


def _collect_ref_update_files(root: Path) -> list[Path]:
    """Resolve the ref-update globs to concrete file paths."""
    files: list[Path] = []
    for pattern in _ref_update_globs():
        # pathlib.glob on Windows needs forward-slash patterns
        for p in sorted(root.glob(pattern)):
            if p.is_file() and p not in files:
                files.append(p)
    return files


# ---------------------------------------------------------------------------
# Verification scan paths
# ---------------------------------------------------------------------------

_VERIFY_GLOBS: list[str] = [
    ".claude/skills/**/*.md",
    ".claude/commands/**/*.md",
    "CLAUDE.md",
    "docs/**/*.md",
    "scripts/**/*.py",
    "templates/**/*.md",
    "canon/**/*.md",
]


def _collect_verify_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in _VERIFY_GLOBS:
        for p in sorted(root.glob(pattern)):
            if p.is_file() and p not in files:
                files.append(p)
    return files


# ---------------------------------------------------------------------------
# Content transformation
# ---------------------------------------------------------------------------

def _apply_ref_replacements(content: str) -> str:
    """Apply all reference replacements to *content* and return the result."""
    # Handle the special bible/ directory description line first
    content = _BIBLE_DIR_DESCRIPTION.sub(_BIBLE_DIR_REPLACEMENT, content)

    for old, new in REF_REPLACEMENTS:
        content = content.replace(old, new)
    return content


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

def _dry_run(root: Path) -> str:
    """Return a human-readable report of planned operations."""
    lines: list[str] = ["Migration Plan (dry run)", "=" * 60, ""]

    # File moves / deletes
    lines.append("File Operations:")
    lines.append("-" * 40)
    for op in _build_ops():
        src_abs = root / op.src
        exists = src_abs.exists()
        status = "EXISTS" if exists else "MISSING"
        if op.dst is None:
            lines.append(f"  DELETE  {op.src}  [{status}]")
        elif op.merge:
            lines.append(f"  MERGE   {op.src} -> {op.dst}  [{status}]")
        else:
            lines.append(f"  MOVE    {op.src} -> {op.dst}  [{status}]")

    lines.append("")

    # Reference updates
    lines.append("Reference Updates:")
    lines.append("-" * 40)
    ref_files = _collect_ref_update_files(root)
    change_count = 0
    for fpath in ref_files:
        try:
            original = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        updated = _apply_ref_replacements(original)
        if updated != original:
            rel = fpath.relative_to(root)
            lines.append(f"  UPDATE  {rel}")
            change_count += 1
    if change_count == 0:
        lines.append("  (no reference changes detected)")

    lines.append("")
    lines.append("Replacement Rules:")
    lines.append("-" * 40)
    for old, new in REF_REPLACEMENTS:
        lines.append(f"  {old!r} -> {new!r}")

    lines.append("")
    lines.append(f"Total file operations: {len(_build_ops())}")
    lines.append(f"Total files with ref updates: {change_count}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Execute (atomic)
# ---------------------------------------------------------------------------

@dataclass
class _FileSnapshot:
    """In-memory backup of a single file."""
    rel_path: Path
    content: bytes | None  # None means the file did not exist
    existed: bool


def _snapshot_file(root: Path, rel: Path) -> _FileSnapshot:
    abs_path = root / rel
    if abs_path.exists():
        return _FileSnapshot(rel_path=rel, content=abs_path.read_bytes(), existed=True)
    return _FileSnapshot(rel_path=rel, content=None, existed=False)


def _restore_snapshot(root: Path, snap: _FileSnapshot) -> None:
    abs_path = root / snap.rel_path
    if snap.existed and snap.content is not None:
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_bytes(snap.content)
    elif not snap.existed and abs_path.exists():
        abs_path.unlink()


def _build_rollback_manifest(
    snapshots: list[_FileSnapshot],
    timestamp: str,
) -> dict[str, Any]:
    """Build a dict suitable for YAML serialisation."""
    entries: list[dict[str, Any]] = []
    for snap in snapshots:
        entry: dict[str, Any] = {
            "path": str(snap.rel_path),
            "existed": snap.existed,
        }
        if snap.content is not None:
            try:
                entry["content"] = snap.content.decode("utf-8")
            except UnicodeDecodeError:
                # Store as latin-1 as a safe fallback for binary
                entry["content"] = snap.content.decode("latin-1")
                entry["encoding"] = "latin-1"
        else:
            entry["content"] = None
        entries.append(entry)
    return {
        "migration": "bible_to_canon",
        "timestamp": timestamp,
        "files": entries,
    }


def _execute(root: Path) -> None:
    """Perform the migration atomically.

    1. Read all affected files into memory (snapshots).
    2. Write rollback manifest.
    3. Perform file operations.
    4. On ANY failure, restore from in-memory snapshots and re-raise.
    """
    ops = _build_ops()
    ref_files = _collect_ref_update_files(root)
    timestamp = datetime.now(timezone.utc).isoformat()

    # ---- Phase 1: snapshot everything we will touch ----
    all_rel_paths: list[Path] = []
    for op in ops:
        all_rel_paths.append(op.src)
        if op.dst is not None:
            all_rel_paths.append(op.dst)
    for fpath in ref_files:
        all_rel_paths.append(fpath.relative_to(root))

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_paths: list[Path] = []
    for p in all_rel_paths:
        key = str(p)
        if key not in seen:
            seen.add(key)
            unique_paths.append(p)

    snapshots = [_snapshot_file(root, rel) for rel in unique_paths]

    # ---- Phase 2: write rollback manifest ----
    manifest_path = root / ".migration-rollback.yaml"
    manifest_data = _build_rollback_manifest(snapshots, timestamp)
    try:
        manifest_path.write_text(_dump_yaml(manifest_data), encoding="utf-8")
    except OSError as exc:
        raise MigrationError(f"Failed to write rollback manifest: {exc}") from exc

    # ---- Phase 3: execute operations ----
    try:
        # 3a. File moves / merges / deletes
        for op in ops:
            src_abs = root / op.src
            if not src_abs.exists():
                # Source missing – skip silently (may already have been moved)
                continue

            if op.dst is None:
                # Delete
                src_abs.unlink()
            elif op.merge:
                # Merge: append src content to dst
                dst_abs = root / op.dst
                src_text = src_abs.read_text(encoding="utf-8")
                if dst_abs.exists():
                    dst_text = dst_abs.read_text(encoding="utf-8")
                    # Ensure separation
                    if not dst_text.endswith("\n"):
                        dst_text += "\n"
                    merged = dst_text + "\n" + src_text
                else:
                    dst_abs.parent.mkdir(parents=True, exist_ok=True)
                    merged = src_text
                dst_abs.write_text(merged, encoding="utf-8")
                src_abs.unlink()
            else:
                # Move
                dst_abs = root / op.dst
                dst_abs.parent.mkdir(parents=True, exist_ok=True)
                if dst_abs.exists():
                    dst_abs.unlink()
                shutil.move(str(src_abs), str(dst_abs))

        # 3b. Remove bible/ directory if empty
        bible_dir = root / "bible"
        if bible_dir.is_dir():
            try:
                bible_dir.rmdir()  # only succeeds if empty
            except OSError:
                pass  # non-empty – leave it

        # 3c. Reference updates in-place
        for fpath in ref_files:
            if not fpath.exists():
                continue
            try:
                original = fpath.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            updated = _apply_ref_replacements(original)
            if updated != original:
                fpath.write_text(updated, encoding="utf-8")

    except Exception as exc:
        # ---- Rollback from in-memory snapshots ----
        for snap in snapshots:
            try:
                _restore_snapshot(root, snap)
            except OSError:
                pass  # best-effort restore
        # Clean up manifest since we rolled back
        if manifest_path.exists():
            try:
                manifest_path.unlink()
            except OSError:
                pass
        raise MigrationError(
            f"Migration failed and has been rolled back: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Rollback from manifest
# ---------------------------------------------------------------------------

def _rollback(root: Path) -> None:
    """Restore all files from the rollback manifest."""
    manifest_path = root / ".migration-rollback.yaml"
    if not manifest_path.exists():
        raise MigrationError(
            f"Rollback manifest not found: {manifest_path}"
        )

    raw = manifest_path.read_text(encoding="utf-8")
    data = _load_yaml(raw)
    if not isinstance(data, dict) or "files" not in data:
        raise MigrationError("Invalid rollback manifest format")

    files_list = data["files"]
    if not isinstance(files_list, list):
        raise MigrationError("Invalid rollback manifest: 'files' is not a list")

    for entry in files_list:
        rel = Path(entry["path"])
        existed = entry.get("existed", False)
        content = entry.get("content")
        encoding = entry.get("encoding", "utf-8")
        abs_path = root / rel

        if existed and content is not None:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_bytes(content.encode(encoding))
        elif not existed and abs_path.exists():
            abs_path.unlink()

    # Clean up bible/ directory if it was recreated and is now populated
    # (the snapshots handle individual files; the directory gets
    # recreated automatically by parent.mkdir)

    # Remove the manifest after successful rollback
    manifest_path.unlink()


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

_BIBLE_REF_PATTERN = re.compile(r"bible/", re.IGNORECASE)


# Files that legitimately reference "bible/" because they describe the migration.
_VERIFY_EXCLUDE_NAMES = {
    "implementation_plan.md",
    "phase0_detailed_plan.md",
    "walkthrough.md",
    "task.md",
    "migrate_bible_to_canon.py",
    "test_migration.py",
    "test_no_bible_refs.py",
}


def _verify(root: Path) -> MigrationResult:
    """Scan the repo for residual bible/ references.

    Excludes files that legitimately discuss the migration itself (plan docs,
    the migration script, migration tests).
    """
    files = _collect_verify_files(root)
    remaining_refs: list[dict[str, str]] = []
    files_scanned = 0

    for fpath in files:
        if fpath.name in _VERIFY_EXCLUDE_NAMES:
            continue
        files_scanned += 1
        try:
            content = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(content.splitlines(), start=1):
            if _BIBLE_REF_PATTERN.search(line):
                remaining_refs.append({
                    "file": str(fpath.relative_to(root)),
                    "line_number": str(i),
                    "content": line.strip(),
                })

    ok = len(remaining_refs) == 0
    report: dict[str, Any] = {
        "files_scanned": files_scanned,
        "remaining_refs": remaining_refs,
    }

    # Add counts by file class
    class_counts: dict[str, int] = {}
    for ref in remaining_refs:
        # Derive class from top-level directory or filename
        parts = Path(ref["file"]).parts
        file_class = parts[0] if len(parts) > 1 else ref["file"]
        class_counts[file_class] = class_counts.get(file_class, 0) + 1
    report["counts_by_class"] = class_counts

    return MigrationResult(ok=ok, report=report)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_migration(
    root: Path,
    *,
    dry_run: bool = False,
    execute: bool = False,
    rollback: bool = False,
    verify: bool = False,
) -> str | MigrationResult | None:
    """Main entry point — importable for testing.

    Returns:
        - str          for dry_run (human-readable report)
        - MigrationResult  for verify
        - None         for execute / rollback on success

    Raises:
        MigrationError on failure.
        ValueError     on invalid argument combinations.
    """
    root = root.resolve()

    mode_count = sum([dry_run, execute, rollback, verify])
    if mode_count == 0:
        raise ValueError("Specify one of --dry-run, --execute, --rollback, or --verify")
    if mode_count > 1:
        raise ValueError("Specify only one mode at a time")

    if dry_run:
        return _dry_run(root)
    elif execute:
        _execute(root)
        return None
    elif rollback:
        _rollback(root)
        return None
    elif verify:
        return _verify(root)

    # Unreachable
    return None  # pragma: no cover


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Migrate fiction-writing project from bible/ to canon/ structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s --dry-run                 Show planned changes
              %(prog)s --execute                 Perform migration (atomic)
              %(prog)s --rollback                Revert from .migration-rollback.yaml
              %(prog)s --verify                  Scan for residual bible/ refs
              %(prog)s --execute --root ./myproj Run against a specific project
        """),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Show mapping report without touching files.",
    )
    mode.add_argument(
        "--execute",
        action="store_true",
        help="Perform the migration (atomic with rollback on failure).",
    )
    mode.add_argument(
        "--rollback",
        action="store_true",
        help="Revert from .migration-rollback.yaml manifest.",
    )
    mode.add_argument(
        "--verify",
        action="store_true",
        help="Scan repo for residual bible/ references.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        metavar="PATH",
        help="Project root directory (default: current directory).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        result = run_migration(
            root=args.root,
            dry_run=args.dry_run,
            execute=args.execute,
            rollback=args.rollback,
            verify=args.verify,
        )
    except MigrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if isinstance(result, str):
        # dry-run report
        print(result)
        return 0
    elif isinstance(result, MigrationResult):
        # verify report
        rep = result.report
        print(f"Files scanned: {rep['files_scanned']}")
        refs = rep.get("remaining_refs", [])
        if refs:
            print(f"Remaining bible/ references: {len(refs)}")
            print()
            counts = rep.get("counts_by_class", {})
            if counts:
                print("Counts by file class:")
                for cls, cnt in sorted(counts.items()):
                    print(f"  {cls}: {cnt}")
                print()
            print("Details:")
            for ref in refs:
                line_content = ref['content']
                try:
                    print(f"  {ref['file']}:{ref['line_number']}  {line_content}")
                except UnicodeEncodeError:
                    # Handle console encoding limitations (e.g. Windows cp1252)
                    safe = line_content.encode("ascii", errors="replace").decode("ascii")
                    print(f"  {ref['file']}:{ref['line_number']}  {safe}")
            return 1
        else:
            print("OK: No residual bible/ references found.")
            return 0
    else:
        # execute / rollback success
        if args.execute:
            print("Migration completed successfully.")
            print("Rollback manifest saved to .migration-rollback.yaml")
        elif args.rollback:
            print("Rollback completed successfully.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
