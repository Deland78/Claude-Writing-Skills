# Phase 1 Acceptance Checklist

All items must be green before Phase 2A begins.

## Automated Checks

- [ ] `python scripts/validate_coauthor_setup.py --root .` — all checks pass
- [ ] `python scripts/schema_validator.py --all` — all schemas parse (10+)
- [ ] `python scripts/relationship_query.py --validate --file canon/relationships.yaml` — validates clean
- [ ] `pytest tests/` — all tests pass

## Skills Implemented

- [ ] `.claude/skills/story-concept/SKILL.md` exists with YAML frontmatter
- [ ] `.claude/skills/story-arc-builder/SKILL.md` exists with YAML frontmatter
- [ ] `.claude/skills/act-outline/SKILL.md` exists with YAML frontmatter
- [ ] All three skills are discoverable via `/project:skills:*`

## Schemas

- [ ] `schemas/story_concept_input.schema.yaml` — validates concept inputs
- [ ] `schemas/story_arc_input.schema.yaml` — validates arc inputs
- [ ] `schemas/act_outline_input.schema.yaml` — validates outline inputs
- [ ] All example inputs pass validation

## Templates

- [ ] `templates/story-concept.template.md` — contains all L1 required headings
- [ ] `templates/story-arc.template.md` — contains all L2 required headings
- [ ] `templates/act-outline.template.md` — contains all L3 required headings
- [ ] Golden examples match template heading requirements

## Pipeline Integration

- [ ] `.claude/commands/pipeline-run.md` includes Stage 0 (Steps 0A/0B/0C)
- [ ] `CLAUDE.md` references new skills and paths
- [ ] `README.md` includes Stage 0 getting-started path
- [ ] `.pipeline-state.yaml` state transitions documented in pipeline-run.md

## Regression

- [ ] `pytest tests/test_no_bible_refs.py` — no stale bible/ references
- [ ] No forbidden vocabulary in skill definitions

## End-to-End Readiness

- [ ] Skills write to correct output paths:
  - `canon/story-concept.md` (L1)
  - `canon/story-arc.md` (L2)
  - `canon/acts/act-{N}-outline.md` (L3)
- [ ] Each skill documents its state transition
- [ ] story-concept incorporates story-promise framework
- [ ] Smoke trace exists at `traces/phase1-smoke.trace.md` (populated after manual run)

## Git Tags

- [ ] `phase1/p1.7` tag applied after all checks pass
