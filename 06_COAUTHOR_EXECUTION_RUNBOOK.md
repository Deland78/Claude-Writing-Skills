# AI Co-Author Execution Runbook

## Objective
Operationalize the AI co-author plan into a repeatable, validated workflow that can run with human checkpoints, automatic diagnostics, and long-term preference memory.

## Deliverables Included
1. Canon registry and module folders under `canon/`.
2. Style sample intake folder with minimum 3 examples.
3. Setup validator script: `scripts/validate_coauthor_setup.py`.

## How to Use
1. Add or replace files in `canon/style-samples/` with your own voice samples.
2. Keep at least 3 markdown files.
3. Update canonical modules (`characters`, `world`, `tech`, `themes`, `timeline`) as the story evolves.
4. Run:

```bash
python scripts/validate_coauthor_setup.py --root .
```

5. Resolve any failing checks before running drafting or analysis stages.

## Validation Rules
- `canon/index.md` exists and acts as canonical registry.
- `canon/timeline.md` exists.
- `canon/preferences.md` exists.
- Required module directories exist.
- `canon/style-samples/` contains at least 3 `.md` files.

## Recommended Workflow
1. Seed concept and constraints.
2. Lock canon baseline in `canon/`.
3. Generate architecture and scene blueprints.
4. Draft scene in user style.
5. Run continuity and trope diagnostics.
6. Present alternatives and pause for approval.
7. Capture accepted preference updates in `canon/preferences.md`.

## Notes
- This runbook intentionally keeps implementation lightweight while enforcing core structure.
- The validator script is deterministic and CI-friendly.
