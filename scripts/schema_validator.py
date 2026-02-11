#!/usr/bin/env python3
"""Shared schema validation utility for the fiction pipeline.

Validates data against JSON Schema 2020-12 YAML schema files.

Usage:
    python scripts/schema_validator.py schemas/agent_comment.schema.yaml data.yaml
    python scripts/schema_validator.py --all
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema
import yaml


SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)


def load_schema(schema_path: Path) -> dict:
    """Load and return a YAML schema file."""
    with open(schema_path) as f:
        return yaml.safe_load(f)


def validate(schema_name: str, data: dict, schemas_dir: Path = SCHEMAS_DIR) -> ValidationResult:
    """Validate data against a named schema.

    Args:
        schema_name: Schema name without extension (e.g., 'agent_comment').
        data: The data to validate.
        schemas_dir: Directory containing schema files.

    Returns:
        ValidationResult with ok=True if valid, or ok=False with error list.
    """
    schema_file = schemas_dir / f"{schema_name}.schema.yaml"
    if not schema_file.exists():
        return ValidationResult(ok=False, errors=[f"Schema file not found: {schema_file}"])

    schema = load_schema(schema_file)
    return validate_against_schema(schema, data)


def validate_against_schema(schema: dict, data: dict) -> ValidationResult:
    """Validate data against a loaded schema dict."""
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema)
    errors = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
        errors.append(f"{path}: {error.message}")
    if errors:
        return ValidationResult(ok=False, errors=errors)
    return ValidationResult(ok=True)


def validate_file(schema_path: Path, data_path: Path) -> ValidationResult:
    """Validate a YAML data file against a schema file."""
    schema = load_schema(schema_path)
    with open(data_path) as f:
        data = yaml.safe_load(f)
    return validate_against_schema(schema, data)


def validate_all(schemas_dir: Path = SCHEMAS_DIR) -> dict[str, ValidationResult]:
    """Validate that all schema files in the directory are well-formed JSON Schema."""
    results = {}
    for schema_file in sorted(schemas_dir.glob("*.schema.yaml")):
        name = schema_file.stem.replace(".schema", "")
        try:
            schema = load_schema(schema_file)
            if "$schema" not in schema:
                results[name] = ValidationResult(ok=False, errors=["Missing $schema field"])
                continue
            if "$id" not in schema:
                results[name] = ValidationResult(ok=False, errors=["Missing $id field"])
                continue
            # Check it's valid JSON Schema by attempting to create a validator
            validator_cls = jsonschema.validators.validator_for(schema)
            validator_cls.check_schema(schema)
            results[name] = ValidationResult(ok=True)
        except jsonschema.SchemaError as e:
            results[name] = ValidationResult(ok=False, errors=[str(e)])
        except Exception as e:
            results[name] = ValidationResult(ok=False, errors=[f"Unexpected error: {e}"])
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate data against fiction pipeline schemas")
    parser.add_argument("schema", nargs="?", help="Path to schema file")
    parser.add_argument("data", nargs="?", help="Path to data file to validate")
    parser.add_argument("--all", action="store_true", help="Validate all schema files are well-formed")
    args = parser.parse_args()

    if args.all:
        results = validate_all()
        failures = 0
        for name, result in results.items():
            if result.ok:
                print(f"OK: {name}")
            else:
                print(f"FAIL: {name}", file=sys.stderr)
                for err in result.errors:
                    print(f"  {err}", file=sys.stderr)
                failures += 1
        if failures:
            print(f"\n{failures} schema(s) failed validation.", file=sys.stderr)
            return 1
        print(f"\nAll {len(results)} schemas valid.")
        return 0

    if not args.schema:
        parser.error("Provide a schema file path, or use --all")

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}", file=sys.stderr)
        return 1

    if not args.data:
        # Just validate the schema itself
        try:
            schema = load_schema(schema_path)
            validator_cls = jsonschema.validators.validator_for(schema)
            validator_cls.check_schema(schema)
            print(f"Schema {schema_path} is valid.")
            return 0
        except Exception as e:
            print(f"Schema {schema_path} is invalid: {e}", file=sys.stderr)
            return 1

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Data file not found: {data_path}", file=sys.stderr)
        return 1

    result = validate_file(schema_path, data_path)
    if result.ok:
        print(f"Validation passed: {data_path}")
        return 0
    else:
        print(f"Validation failed: {data_path}", file=sys.stderr)
        for err in result.errors:
            print(f"  {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
