#!/usr/bin/env bash
# start_step.sh — Zero-friction session start for the fiction pipeline.
# Displays current pipeline state and context manifest.
# Usage: ./scripts/start_step.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$ROOT/.pipeline-state.yaml"

if [ ! -f "$STATE" ]; then
    echo "ERROR: .pipeline-state.yaml not found at $STATE" >&2
    exit 1
fi

# Prefer virtual-env Python, fall back to system.
if [ -f "$ROOT/.venv/bin/python" ]; then
    PYTHON="$ROOT/.venv/bin/python"
elif [ -f "$ROOT/.venv/Scripts/python.exe" ]; then
    PYTHON="$ROOT/.venv/Scripts/python.exe"
else
    PYTHON="python3"
fi

echo "=== Fiction Pipeline — Session Start ==="
echo
"$PYTHON" "$ROOT/scripts/context_loader.py" --state "$STATE" --root "$ROOT"
