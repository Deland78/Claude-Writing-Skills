# AI Co-Author Execution Runbook

Hands-on testing guide for the fiction writing pipeline. This goes deeper than the README Quick Start — it covers exact commands, expected outputs, state transitions, and verification steps.

For directory layout and skill list, see `CLAUDE.md`.

## Objective

Validate that the pipeline tools, canon structure, and Stage 0 skills work end-to-end: validation scripts pass, story-concept/arc/outline skills produce correct canon artifacts, pipeline state advances correctly, and mob review sessions run the 4-phase protocol.

## Prerequisites

### Canon structure

These paths must exist before running any pipeline work. Create missing directories with `mkdir -p`; populate files from their templates in `templates/`.

| Path | Purpose | Template |
|------|---------|----------|
| `canon/index.md` | Canonical registry | — |
| `canon/timeline.md` | Scene/chapter continuity tracker | `templates/scene-tracker.template.md` |
| `canon/preferences.md` | User style and content preferences | — |
| `canon/relationships.yaml` | Entity-relationship graph | — |
| `canon/characters/` | Character profiles | `templates/character-profile.template.md` |
| `canon/world/` | World docs: `story-bible.md`, `world-rules.md` | `templates/story-bible.template.md`, `templates/world-rules.template.md` |
| `canon/tech/` | Technology/system documentation | — |
| `canon/themes/` | Thematic tracking | — |
| `canon/acts/` | Act outlines (populated by Stage 0) | `templates/act-outline.template.md` |
| `canon/style-samples/` | At least 3 `.md` files of your prose for voice modeling | — |

### Pipeline state

`.pipeline-state.yaml` must exist at the project root. A fresh state looks like:

```yaml
position:
  level: L1
  act: null
  chapter: null
  scene: null
mode: manual
canon_version: 1
```

The file also contains agent configuration (`agents:`) and mob session settings (`mob_config:`). See `schemas/pipeline_state.schema.yaml` for the full contract.

### Style samples

The `canon/style-samples/` directory needs at least 3 `.md` files. These should be examples of your existing prose — writing that represents the voice you want the system to model. The validation script checks this minimum.

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate_coauthor_setup.py` | Structural validation (14 checks) |
| `scripts/schema_validator.py` | JSON Schema 2020-12 validation for all `.schema.yaml` files |
| `scripts/relationship_query.py` | Relationship querying, mutation, and semantic validation |
| `scripts/context_loader.py` | Context manifest generation by pipeline level |
| `scripts/trace_renderer.py` | Render mob session trace JSON to markdown |

## Validation

Run all three validation commands before starting any pipeline work. All three must pass.

### 1. Structural validation (14 checks)

```bash
python scripts/validate_coauthor_setup.py --root .
```

This checks:

| # | Check | What it verifies |
|---|-------|-----------------|
| 1 | `canon/index.md` | File exists |
| 2 | `canon/timeline.md` | File exists |
| 3 | `canon/preferences.md` | File exists |
| 4 | `canon/relationships.yaml` | File exists |
| 5 | `canon/characters/` | Directory exists |
| 6 | `canon/world/` | Directory exists |
| 7 | `canon/tech/` | Directory exists |
| 8 | `canon/themes/` | Directory exists |
| 9 | `canon/style-samples/` | Directory exists |
| 10 | `canon/acts/` | Directory exists |
| 11 | `.pipeline-state.yaml` | File exists |
| 12 | `schemas/*.schema.yaml` | At least 1 schema file in `schemas/` |
| 13 | No stale `bible/` refs | Skills and `CLAUDE.md` don't reference the old `bible/` path |
| 14 | Style sample count | >= 3 `.md` files in `canon/style-samples/` |

Expected output when passing:
```
PASS: Canon index exists (canon/index.md)
PASS: Canon timeline exists (canon/timeline.md)
...
PASS: style sample count is 3 (minimum 3)

Validation passed.
```

Any FAIL lines print to stderr. Fix all failures before proceeding.

### 2. Schema validation (10 schemas)

```bash
python scripts/schema_validator.py --all
```

Validates every `.schema.yaml` file in `schemas/` is well-formed JSON Schema 2020-12. Checks that each file has `$schema` and `$id` fields and parses without errors.

Current schemas: `act_outline_input`, `agent_comment`, `commit_patch`, `continuity_report`, `node_input`, `pipeline_state`, `relationships`, `story_arc_input`, `story_concept_input`, `trace_record`.

Expected output:
```
OK: act_outline_input
OK: agent_comment
...
All 10 schemas valid.
```

To validate a single schema: `python scripts/schema_validator.py schemas/pipeline_state.schema.yaml`

To validate data against a schema: `python scripts/schema_validator.py schemas/pipeline_state.schema.yaml .pipeline-state.yaml`

### 3. Relationship integrity

```bash
python scripts/relationship_query.py --validate --file canon/relationships.yaml
```

Runs semantic validation:
- No duplicate relationship IDs
- No alias collisions across entities
- Every `rel` value is in the file's `rel_vocabulary`
- Supersession bidirectional consistency (`supersedes` / `superseded_by` match)
- Circular supersession detection
- Temporal overlap for identical `(from, to, rel)` triples
- `valid_from` / `valid_to` format: `Act{N}/Ch{M}` or `L{N}/{word}`
- `source` citation format: `canon/...md` (with optional `#L{N}` anchor)

Expected output: `Validation passed.`

### Full test suite (optional)

```bash
pytest tests/ -v
```

Runs 14 test modules including schema validation, relationship tests, context loader, migration regression, template validation, and the `bible/` reference check.

## Stage 0: Story Development (L1 → L2 → L3)

This is the foundation. Each step produces a canon artifact and advances `.pipeline-state.yaml`. Run the steps in order — each skill checks that its prerequisites exist.

### Step 1: Story Concept (L1)

```
/project:skills:story-concept
```

- **Required inputs**: `genre`, `protagonist`, `inciting_situation` (prompted interactively)
- **Optional inputs**: `comparable_titles`, `world_premise`, `target_length`
- **Context loaded**: `canon/world/story-bible.md`, `canon/preferences.md`, `templates/story-concept.template.md`
- **Output**: `canon/story-concept.md`
- **State transition**: `position.level` stays at `L1` until you advance to arc building

**PAUSE** — Read `canon/story-concept.md` end to end. Check:
- [ ] Controlling idea is clear and specific
- [ ] CDQ (Central Dramatic Question) drives narrative tension
- [ ] Genre conventions are identified
- [ ] Story Promise framework is populated

### Step 2: Story Arc (L2)

```
/project:skills:story-arc-builder
```

- **Required input**: Reads `canon/story-concept.md` (fails if missing)
- **Optional inputs**: `target_scope`, `act_count` (default: 4), `character_files`
- **Context loaded**: `canon/story-concept.md`, `canon/relationships.yaml`, `canon/characters/*.md`, `canon/preferences.md`
- **Output**: `canon/story-arc.md` (act progression, character trajectories, subplot map, thematic pressure points)
- **State transition**: `position.level` advances to `L2`

**PAUSE** — Read `canon/story-arc.md` end to end. Check:
- [ ] Act boundaries align with story structure
- [ ] Character trajectories track growth/change
- [ ] Subplot map connects to main arc
- [ ] Thematic pressure points escalate

### Step 3: Act Outlines (L3, per act)

```
/project:skills:act-outline
```

Run once per act (prompted for act number).

- **Required input**: Reads `canon/story-arc.md` (fails if missing), act number
- **Optional input**: `chapter_count_hint`
- **Context loaded**: `canon/story-arc.md`, `canon/story-concept.md`, sibling `canon/acts/act-*-outline.md`, `canon/characters/*.md`, `canon/relationships.yaml`
- **Output**: `canon/acts/act-{N}-outline.md` (chapter beats, value shifts, causal dependencies)
- **State transition**: `position.level` = `L3`, `position.act` = `N`

**PAUSE** after each act — Read `canon/acts/act-{N}-outline.md`. Check:
- [ ] Chapter beats follow Five Commandments structure
- [ ] Value shifts are explicit per chapter
- [ ] Causal dependencies connect chapters logically
- [ ] Continuity touchpoints reference existing canon

### Verification after Stage 0

```bash
# Confirm artifacts exist
ls canon/story-concept.md canon/story-arc.md canon/acts/

# Check pipeline state
python scripts/schema_validator.py schemas/pipeline_state.schema.yaml .pipeline-state.yaml

# Check context manifest at current level
python scripts/context_loader.py --state .pipeline-state.yaml --root .

# Validate relationships if any were added
python scripts/relationship_query.py --validate --file canon/relationships.yaml

# Run tests
pytest tests/ -v
```

### Pipeline state after Stage 0

| After step | `position.level` | `position.act` | Ready for |
|------------|:-:|:-:|-----------|
| (start) | L1 | null | Story concept |
| story-concept | L2 | null | Arc building |
| story-arc-builder | L3 | null | Act outlining |
| act-outline(N) | L3 | N | Next act or Stage 1 |
| All acts outlined | L4 | 1 | Chapter planning |

## Mob Review Sessions (Mode C)

At any pipeline step, you can run a mob review where specialist agents critique the current artifact. Mode is per-step — you can alternate between Mode A (direct skill) and Mode C (mob review) freely.

### Running a Mob Session

```
/project:skills:mob-session
```

### What Happens

1. **Phase 1 (Structure Offer)**: Lead Editor organizes input into the step's template format. You approve, adjust, override, or skip.
2. **Phase 2 (Comment Queue)**: Each active agent gives one comment with canon citations. You accept, reject, revise, or park each comment.
3. **Phase 3 (Resolution Check)**: Lead Editor summarizes the round ledger. You choose: another round, commit, or park.
4. **Phase 4 (Commit)**: Approved changes are written to canon files, relationships updated, trace logged.

### Agent Activation by Level

| Agent | L1 | L2 | L3 | L4 | L5 |
|-------|:--:|:--:|:--:|:--:|:--:|
| Lead Editor | Y | Y | Y | Y | Y |
| Plot Analyst | Y | Y | Y | Y | — |
| Character Specialist | — | Y | Y | Y | Y |
| Depth Partner | Y | Y | Y | — | — |
| Continuity Agent | — | — | Y | Y | Y |
| Prose Crafter | — | — | — | Y | Y |

### Governance

- **Max rounds**: 3 (configurable in `.pipeline-state.yaml` → `mob_config.max_rounds`)
- **Budget cap**: $1.00 per session (configurable → `mob_config.budget_cap_usd`)
- **Diminishing returns**: if 0 changes accepted in a round, session prompts to commit
- **Citation enforcement**: comments without `canon/` citations are tagged `[advisory]` and cannot mutate canon without your explicit override

### Mode Switching

| User action | Effect |
|-------------|--------|
| Run a Stage 0 skill directly | Mode A — skill executes, no agent comments |
| Run `/project:skills:mob-session` | Mode C — Lead Editor orchestrates 4-phase protocol |
| Say "just validate this" during mob | Exit to Mode A for this step |
| Say "let's discuss" after Mode A step | Enter Mode C on the artifact just produced |

### Example Workflow

```
1. /project:skills:story-concept     → produces canon/story-concept.md (Mode A)
2. PAUSE: review output
3. /project:skills:mob-session       → agents review the concept (Mode C)
4. /project:skills:story-arc-builder → produces canon/story-arc.md (Mode A)
5. PAUSE: review output
6. /project:skills:mob-session       → agents review the arc (Mode C)
```

### Traces

Mob sessions produce dual-write traces:
- **JSON source**: `traces/{name}.trace.json` (machine-readable)
- **Rendered view**: `traces/{name}.trace.md` (human-readable, includes `<!-- HUMAN-EVAL -->` placeholders)

Render a trace manually:
```bash
python scripts/trace_renderer.py traces/example.trace.json
# Writes traces/example.trace.md
```

Optionally specify output path:
```bash
python scripts/trace_renderer.py traces/example.trace.json --output review/example.md
```

See `docs/mob_protocol.md` for the full protocol specification and `docs/citation_enforcement.md` for citation rules.

## Pipeline Stages 1-3 (Reference)

These skills exist but are not yet smoke-tested as a full pipeline. Listed here for reference — test individually as needed.

### Stage 1: Chapter Planning

```
/project:skills:chapter-promise    # Define chapter narrative promise
/project:skills:tension-curve      # Map micro-tension beats
/project:skills:scene-architect    # Convert to structured scene cards
```

### Stage 2: Drafting

```
/project:skills:voice-anchor       # Establish/verify narrative voice
/project:skills:scene-draft        # Generate full prose
```

### Stage 3: Revision

Run in sequence:
```
/project:skills:character-truth       # Audit character consistency
/project:skills:dialogue-subtext      # Enhance dialogue with subtext
/project:skills:line-tightening       # Compress prose 10-20%
/project:skills:ai-filter-humanize    # Remove AI fingerprints
/project:skills:continuity-callback   # Validate continuity, add callbacks
/project:skills:final-polish          # Final editorial pass
```

To run the full pipeline from current state: `/project:pipeline-run`

## Troubleshooting

### Validation fails on style samples

Add at least 3 `.md` files to `canon/style-samples/`. These should be examples of your prose style — existing writing that represents the voice you want. The minimum is configurable:

```bash
python scripts/validate_coauthor_setup.py --root . --min-style-samples 5
```

### Schema validation errors

Run the specific schema to see the parse error:
```bash
python scripts/schema_validator.py schemas/pipeline_state.schema.yaml
```

Common issues: missing `$schema` or `$id` fields, invalid type definitions.

### Stale `bible/` references

The system migrated from `bible/` to `canon/` in Phase 0. If validation flags stale refs, update the file to use `canon/` paths. The regression test covers skills, CLAUDE.md, docs, canon, and templates:

```bash
pytest tests/test_no_bible_refs.py -v
```

Files that legitimately describe the migration (e.g., `docs/phase0_detailed_plan.md`) are excluded.

### Pipeline state stuck or wrong

Check `.pipeline-state.yaml` directly. The `position.level` and `position.act` fields track where you are. Validate it against the schema:

```bash
python scripts/schema_validator.py schemas/pipeline_state.schema.yaml .pipeline-state.yaml
```

If state is wrong, edit the file manually and re-validate. The `position.level` must be one of `L1`-`L5`.

### Relationship validation errors

Common causes:
- **Duplicate IDs**: two relationships share the same `rel_NNN` ID
- **Vocabulary mismatch**: `rel` value not in the file's `rel_vocabulary` section
- **Citation format**: `source` must match `canon/...md` (with optional `#L{N}` anchor)
- **Temporal overlap**: two relationships with the same `(from, to, rel)` triple have overlapping `valid_from`/`valid_to` ranges

Run with verbose output:
```bash
python scripts/relationship_query.py --validate --file canon/relationships.yaml
```

### Context manifest looks wrong

Check what the context loader generates for the current pipeline level:

```bash
python scripts/context_loader.py --state .pipeline-state.yaml --root .
```

This shows every file that would be loaded, whether it exists, estimated token count, and manifest hash. If files are missing, create them from their templates.
