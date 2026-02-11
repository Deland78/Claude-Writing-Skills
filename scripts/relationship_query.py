#!/usr/bin/env python3
"""CLI tool for querying and mutating a YAML entity-relationship file.

Supports querying relationships by entity (with alias resolution and temporal
filtering), adding new relationships with vocabulary validation, full semantic
validation, and rendering a markdown adjacency matrix.

Usage:
    python scripts/relationship_query.py query --entity NAME [--as-of POS] --file PATH
    python scripts/relationship_query.py add --from FROM --to TO --rel REL \\
        --context CTX --valid-from POS --confidence CONF --source SRC --file PATH
    python scripts/relationship_query.py render-matrix [--as-of POS] --file PATH
    python scripts/relationship_query.py --validate --file PATH
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class VocabularyError(ValueError):
    """Raised when a relationship term is not in the controlled vocabulary."""


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """Outcome of a semantic validation pass."""

    ok: bool
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Temporal position helpers
# ---------------------------------------------------------------------------

_ACT_CH_RE = re.compile(r"^Act(\d+)/Ch(\d+)$")
_LWORD_RE = re.compile(r"^L(\d+)/(\w+)$")


def parse_position(pos: str) -> tuple[int, int]:
    """Parse a temporal position string into a comparable ``(act, chapter)`` tuple.

    Accepted formats:
        ``Act{N}/Ch{M}`` -- returns ``(N, M)``
        ``L{N}/{word}``  -- returns ``(0, 0)`` (pre-story backstory positions)

    Raises:
        ValueError: If *pos* does not match either format.
    """
    m = _ACT_CH_RE.match(pos)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = _LWORD_RE.match(pos)
    if m:
        return (0, 0)

    raise ValueError(
        f"Invalid position format: {pos!r}. "
        "Expected 'Act{{N}}/Ch{{M}}' or 'L{{N}}/{{word}}'."
    )


# ---------------------------------------------------------------------------
# Vocabulary helpers
# ---------------------------------------------------------------------------

def _flatten_vocabulary(rel_vocabulary: dict[str, list[str]]) -> set[str]:
    """Return the flat set of all allowed relationship terms."""
    terms: set[str] = set()
    for category_terms in rel_vocabulary.values():
        if isinstance(category_terms, list):
            terms.update(category_terms)
    return terms


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load(file_path: str | Path) -> dict[str, Any]:
    """Load a relationships YAML file and return its contents as a dict."""
    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save(data: dict[str, Any], file_path: str | Path) -> None:
    """Write *data* back to a YAML file."""
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _entity_ids_for(data: dict[str, Any], entity: str) -> set[str]:
    """Return a set of entity IDs that *entity* could refer to.

    This includes:
    - The entity ID itself (if it exists as a key in ``data["entities"]``).
    - Any entity whose alias list contains *entity*.
    """
    entities = data.get("entities", {})
    ids: set[str] = set()

    # Direct key match.
    if entity in entities:
        ids.add(entity)

    # Alias match -- find any entity whose aliases include *entity*.
    for eid, einfo in entities.items():
        aliases = einfo.get("aliases", [])
        if entity in aliases:
            ids.add(eid)

    return ids


def query(
    data: dict[str, Any],
    entity: str,
    as_of: str | None = None,
) -> list[dict[str, Any]]:
    """Return relationships involving *entity* (by ID or alias).

    Parameters
    ----------
    data:
        Loaded relationships dict.
    entity:
        Entity ID or alias string to search for.
    as_of:
        Optional temporal position (``Act{N}/Ch{M}`` or ``L{N}/{word}``).
        When provided, only relationships active at that point are returned.
    """
    # Resolve entity to a set of canonical entity IDs.
    match_ids = _entity_ids_for(data, entity)

    # Also allow a direct string match on from/to for convenience (in case
    # an alias string is used directly in a relationship record).
    match_strings: set[str] = {entity} | match_ids

    # Collect aliases of every matched entity so we can also match those.
    entities = data.get("entities", {})
    for eid in list(match_ids):
        aliases = entities.get(eid, {}).get("aliases", [])
        match_strings.update(aliases)

    as_of_pos: tuple[int, int] | None = None
    if as_of is not None:
        as_of_pos = parse_position(as_of)

    results: list[dict[str, Any]] = []
    for rel in data.get("relationships", []):
        from_e = rel.get("from", "")
        to_e = rel.get("to", "")

        if from_e not in match_strings and to_e not in match_strings:
            continue

        # Temporal filtering.
        if as_of_pos is not None:
            vf = rel.get("valid_from")
            vt = rel.get("valid_to")
            if vf is not None and parse_position(vf) > as_of_pos:
                continue
            if vt is not None and parse_position(vt) <= as_of_pos:
                continue

        results.append(rel)

    return results


def add(
    data: dict[str, Any],
    from_e: str,
    to_e: str,
    rel: str,
    context: str,
    valid_from: str,
    confidence: str,
    source: str,
    valid_to: str | None = None,
) -> dict[str, Any]:
    """Add a new relationship to *data* and return the new record.

    Raises:
        VocabularyError: If *rel* is not in the file's ``rel_vocabulary``.
    """
    vocab = _flatten_vocabulary(data.get("rel_vocabulary", {}))
    if rel not in vocab:
        raise VocabularyError(
            f"Relationship term {rel!r} is not in the controlled vocabulary. "
            f"Allowed terms: {sorted(vocab)}"
        )

    # Determine next ID.
    existing_ids: list[int] = []
    for r in data.get("relationships", []):
        m = re.match(r"^rel_(\d+)$", r.get("id", ""))
        if m:
            existing_ids.append(int(m.group(1)))
    next_num = max(existing_ids, default=0) + 1
    new_id = f"rel_{next_num:03d}"

    new_rel: dict[str, Any] = {
        "id": new_id,
        "from": from_e,
        "to": to_e,
        "rel": rel,
        "context": context,
        "valid_from": valid_from,
        "confidence": confidence,
        "source": source,
    }
    if valid_to is not None:
        new_rel["valid_to"] = valid_to

    data.setdefault("relationships", []).append(new_rel)
    return new_rel


# ---------------------------------------------------------------------------
# Semantic validation
# ---------------------------------------------------------------------------

_VALID_FROM_RE = re.compile(r"^(L\d+/\w+|Act\d+/Ch\d+)$")
_SOURCE_RE = re.compile(r"^canon/.+\.md(#L\d+)?$")


def validate_relationships(data: dict[str, Any]) -> ValidationResult:
    """Run full semantic validation on a relationships data structure.

    Checks performed:
    - No duplicate relationship IDs
    - No alias collisions across entities
    - Every ``rel`` matches a term in ``rel_vocabulary``
    - Supersession bidirectional consistency
    - Circular supersession detection
    - Temporal overlap for identical ``(from, to, rel)`` triples
    - Source citation format
    - ``valid_from`` / ``valid_to`` format
    """
    errors: list[str] = []
    vocab = _flatten_vocabulary(data.get("rel_vocabulary", {}))
    relationships: list[dict[str, Any]] = data.get("relationships", [])
    entities: dict[str, Any] = data.get("entities", {})

    # -- Duplicate relationship IDs ----------------------------------------
    seen_ids: dict[str, int] = {}
    for idx, r in enumerate(relationships):
        rid = r.get("id", f"<missing@{idx}>")
        if rid in seen_ids:
            errors.append(f"Duplicate relationship ID: {rid}")
        else:
            seen_ids[rid] = idx

    # -- Alias collisions across entities ----------------------------------
    alias_owner: dict[str, str] = {}
    for eid, einfo in entities.items():
        for alias in einfo.get("aliases", []):
            if alias in alias_owner:
                errors.append(
                    f"Alias collision: '{alias}' is claimed by both "
                    f"'{alias_owner[alias]}' and '{eid}'"
                )
            else:
                alias_owner[alias] = eid

    # -- Per-relationship checks -------------------------------------------
    rel_by_id: dict[str, dict[str, Any]] = {r["id"]: r for r in relationships if "id" in r}

    for r in relationships:
        rid = r.get("id", "<unknown>")

        # rel in vocabulary
        if r.get("rel") not in vocab:
            errors.append(f"{rid}: rel '{r.get('rel')}' not in rel_vocabulary")

        # valid_from format
        vf = r.get("valid_from", "")
        if not _VALID_FROM_RE.match(str(vf)):
            errors.append(f"{rid}: invalid valid_from format: {vf!r}")

        # valid_to format (if present and not null)
        vt = r.get("valid_to")
        if vt is not None and not _VALID_FROM_RE.match(str(vt)):
            errors.append(f"{rid}: invalid valid_to format: {vt!r}")

        # source format
        src = r.get("source", "")
        if not _SOURCE_RE.match(str(src)):
            errors.append(f"{rid}: invalid source format: {src!r}")

        # Supersession bidirectional consistency
        supersedes = r.get("supersedes")
        if supersedes is not None:
            target = rel_by_id.get(supersedes)
            if target is None:
                errors.append(
                    f"{rid}: supersedes '{supersedes}' which does not exist"
                )
            elif target.get("superseded_by") != rid:
                errors.append(
                    f"{rid}: supersedes '{supersedes}', but "
                    f"'{supersedes}'.superseded_by = {target.get('superseded_by')!r} "
                    f"(expected '{rid}')"
                )

        superseded_by = r.get("superseded_by")
        if superseded_by is not None:
            target = rel_by_id.get(superseded_by)
            if target is None:
                errors.append(
                    f"{rid}: superseded_by '{superseded_by}' which does not exist"
                )
            elif target.get("supersedes") != rid:
                errors.append(
                    f"{rid}: superseded_by '{superseded_by}', but "
                    f"'{superseded_by}'.supersedes = {target.get('supersedes')!r} "
                    f"(expected '{rid}')"
                )

    # -- Circular supersession detection -----------------------------------
    for r in relationships:
        rid = r.get("id")
        if rid is None:
            continue
        visited: set[str] = set()
        current: str | None = rid
        while current is not None:
            if current in visited:
                errors.append(f"Circular supersession chain detected involving: {rid}")
                break
            visited.add(current)
            next_rel = rel_by_id.get(current)
            current = next_rel.get("supersedes") if next_rel else None

    # -- Temporal overlap for identical (from, to, rel) triples ------------
    from collections import defaultdict

    triple_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in relationships:
        key = (r.get("from", ""), r.get("to", ""), r.get("rel", ""))
        triple_groups[key].append(r)

    for triple_key, group in triple_groups.items():
        if len(group) < 2:
            continue
        # Compare every pair.
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a = group[i]
                b = group[j]
                try:
                    a_start = parse_position(str(a.get("valid_from", "")))
                    b_start = parse_position(str(b.get("valid_from", "")))
                except ValueError:
                    continue  # Format errors already reported.

                a_end_raw = a.get("valid_to")
                b_end_raw = b.get("valid_to")

                # None means "still active" -- treat as infinity.
                a_end: tuple[int, int] | None = None
                b_end: tuple[int, int] | None = None
                try:
                    if a_end_raw is not None:
                        a_end = parse_position(str(a_end_raw))
                    if b_end_raw is not None:
                        b_end = parse_position(str(b_end_raw))
                except ValueError:
                    continue

                # Overlap: a_start < b_end AND b_start < a_end
                a_before_b_end = (b_end is None) or (a_start < b_end)
                b_before_a_end = (a_end is None) or (b_start < a_end)

                if a_before_b_end and b_before_a_end:
                    errors.append(
                        f"Temporal overlap: {a.get('id')} and {b.get('id')} "
                        f"share ({triple_key[0]}, {triple_key[1]}, {triple_key[2]}) "
                        f"with overlapping validity"
                    )

    return ValidationResult(ok=len(errors) == 0, errors=errors)


# ---------------------------------------------------------------------------
# Matrix rendering
# ---------------------------------------------------------------------------

def render_matrix(data: dict[str, Any], as_of: str | None = None) -> str:
    """Render a markdown adjacency matrix of entity relationships.

    Rows and columns are entity IDs. Cells contain the ``rel`` value(s)
    connecting the row entity (``from``) to the column entity (``to``).
    """
    entities = data.get("entities", {})
    entity_ids = list(entities.keys())

    if not entity_ids:
        return "(no entities defined)"

    # Gather active relationships.
    as_of_pos: tuple[int, int] | None = None
    if as_of is not None:
        as_of_pos = parse_position(as_of)

    # Build cell contents: (from_id, to_id) -> list of rel strings.
    from collections import defaultdict

    cells: dict[tuple[str, str], list[str]] = defaultdict(list)

    for r in data.get("relationships", []):
        if as_of_pos is not None:
            vf = r.get("valid_from")
            vt = r.get("valid_to")
            try:
                if vf is not None and parse_position(vf) > as_of_pos:
                    continue
                if vt is not None and parse_position(vt) <= as_of_pos:
                    continue
            except ValueError:
                continue

        from_e = r.get("from", "")
        to_e = r.get("to", "")
        rel_term = r.get("rel", "")
        cells[(from_e, to_e)].append(rel_term)

    # Build markdown table.
    header = "| From / To |"
    separator = "| --- |"
    for eid in entity_ids:
        header += f" {eid} |"
        separator += " --- |"

    lines: list[str] = [header, separator]
    for row_id in entity_ids:
        row = f"| **{row_id}** |"
        for col_id in entity_ids:
            if row_id == col_id:
                row += " --- |"
            else:
                terms = cells.get((row_id, col_id), [])
                cell_text = ", ".join(terms) if terms else ""
                row += f" {cell_text} |"
        lines.append(row)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="relationship_query",
        description="Query and mutate a YAML entity-relationship file.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run semantic validation on the file and exit.",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to the relationships YAML file.",
    )

    subparsers = parser.add_subparsers(dest="command")

    # -- query -------------------------------------------------------------
    q = subparsers.add_parser("query", help="Query relationships for an entity.")
    q.add_argument("--entity", required=True, help="Entity ID or alias to search for.")
    q.add_argument("--as-of", default=None, help="Temporal position filter (Act1/Ch2).")
    q.add_argument("--file", required=True, dest="query_file", help="Relationships YAML file.")

    # -- add ---------------------------------------------------------------
    a = subparsers.add_parser("add", help="Add a new relationship.")
    a.add_argument("--from", required=True, dest="from_e", help="Source entity ID.")
    a.add_argument("--to", required=True, dest="to_e", help="Target entity ID.")
    a.add_argument("--rel", required=True, help="Relationship term.")
    a.add_argument("--context", required=True, help="Narrative context.")
    a.add_argument("--valid-from", required=True, help="Start position.")
    a.add_argument("--confidence", required=True, choices=["low", "medium", "high"])
    a.add_argument("--source", required=True, help="Canon source reference.")
    a.add_argument("--valid-to", default=None, help="End position (null if omitted).")
    a.add_argument("--file", required=True, dest="add_file", help="Relationships YAML file.")

    # -- render-matrix -----------------------------------------------------
    rm = subparsers.add_parser("render-matrix", help="Render a markdown adjacency matrix.")
    rm.add_argument("--as-of", default=None, help="Temporal position filter.")
    rm.add_argument("--file", required=True, dest="matrix_file", help="Relationships YAML file.")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # -- validate mode (top-level flag) ------------------------------------
    if args.validate:
        file_path = args.file
        if not file_path:
            parser.error("--validate requires --file")
        data = load(file_path)
        result = validate_relationships(data)
        if result.ok:
            print("Validation passed.")
            return 0
        else:
            print("Validation failed:", file=sys.stderr)
            for err in result.errors:
                print(f"  {err}", file=sys.stderr)
            return 1

    # -- subcommands -------------------------------------------------------
    if args.command == "query":
        data = load(args.query_file)
        results = query(data, args.entity, as_of=args.as_of)
        if not results:
            print("No matching relationships found.")
            return 0
        for r in results:
            print(yaml.dump(r, default_flow_style=False, sort_keys=False).rstrip())
            print("---")
        return 0

    if args.command == "add":
        data = load(args.add_file)
        try:
            new_rel = add(
                data,
                from_e=args.from_e,
                to_e=args.to_e,
                rel=args.rel,
                context=args.context,
                valid_from=args.valid_from,
                confidence=args.confidence,
                source=args.source,
                valid_to=args.valid_to,
            )
        except VocabularyError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        save(data, args.add_file)
        print(f"Added relationship {new_rel['id']}:")
        print(yaml.dump(new_rel, default_flow_style=False, sort_keys=False).rstrip())
        return 0

    if args.command == "render-matrix":
        data = load(args.matrix_file)
        print(render_matrix(data, as_of=args.as_of))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
