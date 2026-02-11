# Phase 2A Acceptance Checklist

Hard completion gate for Phase 2A: Simulated MOE (MVP).

## Automated Checks

- [ ] `python scripts/validate_coauthor_setup.py --root .` — all checks pass
- [ ] `python scripts/schema_validator.py --all` — all schemas parse (including updated agent_comment)
- [ ] `pytest tests/` — all tests pass (Phase 1 + Phase 2A tests)

## Agent Definitions

- [ ] All 6 agent files exist in `agents/`
- [ ] All specialists have required sections (Scope, Out of Scope, Active Levels, Evidence Rule, Escalation Rule, Model Tier)
- [ ] `docs/agent_contract.md` exists with shared rules
- [ ] `pytest tests/test_agents.py` passes

## Trace System

- [ ] `templates/trace.template.md` exists
- [ ] `scripts/trace_renderer.py` renders JSON → MD
- [ ] `pytest tests/test_trace_renderer.py` passes

## Protocol

- [ ] `.claude/skills/mob-session/SKILL.md` exists with YAML frontmatter
- [ ] `docs/mob_protocol.md` exists with 4-phase description
- [ ] Mob session is discoverable via `/project:skills:mob-session`
- [ ] `pytest tests/test_mob_protocol.py` passes

## Governance

- [ ] `agent_comment.schema.yaml` includes `citation_status` field
- [ ] `docs/citation_enforcement.md` exists
- [ ] `pytest tests/test_governance.py` passes

## Pipeline Integration

- [ ] `pipeline-run.md` includes Mode C section
- [ ] `CLAUDE.md` references agents/ and mob-session skill
- [ ] `README.md` includes mob review instructions

## Regression

- [ ] `pytest tests/test_no_bible_refs.py` — no stale bible/ references
- [ ] All Phase 1 tests still pass (schemas, templates, skills)

## End-to-End Readiness

- [ ] Smoke trace exists at `traces/phase2a-smoke.trace.json` + `.trace.md`
- [ ] Failure modes trace demonstrates advisory tagging and round termination
- [ ] Mob session skill is invocable and follows the 4-phase protocol
