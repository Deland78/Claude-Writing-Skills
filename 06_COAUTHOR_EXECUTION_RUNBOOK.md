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

## Mob Review Sessions (Mode C)

At any pipeline step, you can run a mob review where specialist agents critique the current artifact:

### Running a Mob Session
```bash
# Invoke the mob session skill
/project:skills:mob-session
```

### What Happens
1. **Phase 1 (Structure Offer)**: Lead Editor organizes input into the step's template format. You approve, adjust, or skip.
2. **Phase 2 (Comment Queue)**: Each active agent (Plot Analyst, Character Specialist, Depth Partner, Continuity Agent, Prose Crafter) gives one comment. You accept, reject, revise, or park each comment.
3. **Phase 3 (Resolution Check)**: Lead Editor summarizes the round. You choose: another round, commit, or park.
4. **Phase 4 (Commit)**: Approved changes are written to canon files, relationships updated, trace logged.

### Governance
- Max rounds: 3 (configurable in `.pipeline-state.yaml` → `mob_config.max_rounds`)
- Diminishing returns: if no changes accepted in a round, session prompts to commit
- Citation enforcement: comments without `canon/` citations are tagged `[advisory]` and cannot mutate canon without your override

### Example Workflow
```
1. /project:skills:story-concept  → produces canon/story-concept.md (Mode A)
2. /project:skills:mob-session    → agents review the concept (Mode C)
3. /project:skills:story-arc-builder → produces canon/story-arc.md (Mode A)
4. /project:skills:mob-session    → agents review the arc (Mode C)
```

See `docs/mob_protocol.md` for the full protocol specification.

## Notes
- This runbook intentionally keeps implementation lightweight while enforcing core structure.
- The validator script is deterministic and CI-friendly.
