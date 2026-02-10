# Unified Fiction Writing Pipeline — Implementation Plan

## Problem Summary

The Fiction Writing Skills System has strong capabilities at the **chapter and scene** levels (12 skills, 3-stage pipeline) but lacks:
- Top-down hierarchical development (Levels 1-3: concept → arcs → act outlines)
- Collaborative human-AI interaction (MOE Mob pattern)
- Context management across multi-step, multi-session work
- Continuity tracking at scale (entity-relationship system)
- Multi-model agent routing

This plan merges the existing MVP Pipeline with the Co-Author vision into a single unified system.

## Confirmed Design Decisions

| Decision | Choice |
|----------|--------|
| Entity-relationship format | **Structured YAML** (not markdown table) |
| Primary execution platform | **Claude Code CLI** (via Antigravity terminal) |
| File editing | **Antigravity editor** |
| Interaction modes | **Mode A** (Manual Driver) + **Mode C** (MOE Mob with Phase 1 structuring) |
| Context strategy | **Conversation = scratch paper, files = memory** |
| Session boundaries | **New conversation per step** (with manifest handoff) |
| Continuity agent | **Sidecar** (separate context, grep/script-based search on YAML) |
| Continuity trigger | **Auto on AI changes, manual on human changes** |
| Source of truth | **`canon/`** directory (migrate from `bible/`) |
| Tracing | **Markdown trace files** (human-annotatable for feedback) |
| Model strategy | **Start cheap, upgrade on eval evidence** |
| Multi-provider | **OpenRouter.ai** support after Claude baseline established |

## Model Strategy

### Start Cheap, Upgrade on Evidence

All agents start at the **lowest viable model tier**. Upgrades happen only when evals show the model is the bottleneck — not preemptively.

| Phase | Agent Models | Rationale |
|-------|-------------|----------|
| **Initial** | All agents on Haiku/Flash | Work out protocol kinks, test orchestration, validate plumbing |
| **After protocol works** | Upgrade agents that eval poorly | If Plot Analyst comments are shallow on Haiku, try Sonnet. Keep Lead Editor on Haiku if it works fine |
| **After Claude baseline** | Test OpenRouter alternatives | Compare Llama, Mistral, Gemini Flash via OpenRouter for agents where Claude offers no quality advantage |

### Agent Model Configuration

Model assignment is stored per-agent in `.pipeline-state.yaml` and can be changed per step.

**Complexity-triggered model floors (C4)**: L1-L3 nodes (concept, arcs, outlines) are load-bearing — everything downstream depends on them. Depth Partner and Character Specialist get a Sonnet floor at these levels:

```yaml
agents:
  lead_editor:
    provider: claude          # claude | openrouter
    model: claude-haiku       # start cheap
    active: true
  plot_analyst:
    provider: claude
    model: claude-haiku       # upgrade to sonnet if evals show need
    active: true
  depth_partner:
    provider: claude
    model: claude-haiku       # baseline
    model_floor:              # (C4) complexity-triggered
      L1: claude-sonnet       # story concept = load-bearing
      L2: claude-sonnet       # arcs = load-bearing
      L3: claude-sonnet       # act outlines = load-bearing
    active: true
  character_specialist:
    provider: claude
    model: claude-haiku
    model_floor:
      L2: claude-sonnet       # arc integrity needs stronger reasoning
      L3: claude-sonnet
    active: true
  continuity_agent:
    provider: claude
    model: claude-haiku       # may stay cheap (tool-heavy)
    active: true
    tool_use: true
  prose_crafter:
    provider: claude
    model: claude-haiku       # upgrade to sonnet for scene drafts
    active: false
```

### OpenRouter Integration

After Claude models establish a quality baseline:
1. The orchestrator's API call layer abstracts the provider (Claude API vs OpenRouter API)
2. Swap one agent at a time to an OpenRouter model
3. Run same eval suite — compare quality scores and cost
4. Keep whichever model delivers best cost/quality ratio per agent

OpenRouter candidates for cost savings:
- **Lead Editor**: Gemini Flash or Llama (orchestration doesn't need frontier)
- **Continuity Agent**: Any cheap model with good tool use
- **Prose Crafter**: Likely stays on Claude (creative writing quality matters most here)

---

## Phase 0: Foundation

Establish the data layer, formal contracts, and restructure before building new features.

---

### I/O Contracts (C1)

#### [NEW] [schemas/](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/schemas)
JSON/YAML schemas for every boundary in the system. All scripts validate against these before advancing state:

| Contract | Validates | When |
|----------|-----------|------|
| `node_input.schema.yaml` | Context + instructions going into each skill/agent call | Before agent call |
| `agent_comment.schema.yaml` | Agent output: comment text, citations, suggested changes | After agent responds |
| `continuity_report.schema.yaml` | Passes/flags/violations with entity refs and evidence | After continuity check |
| `commit_patch.schema.yaml` | Canon changes, relationship adds/changes, citations | Before step commit |
| `trace_record.schema.yaml` | Complete session record with all required fields | After session |
| `relationships.schema.yaml` | Entity registry, rel vocabulary, temporal fields | On any YAML mutation |

Outputs that fail schema validation are **rejected and repaired** (re-prompt with schema + error) before the pipeline advances.

---

### Canon

#### [MODIFY] [canon/](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/canon)
Restructure to support hierarchical story development:

```
canon/
├── story-concept.md          # Level 1 output
├── story-arc.md              # Level 2 output
├── relationships.yaml        # Entity-relationship tracking (NEW)
├── preferences.md            # Existing, keep
├── timeline.md               # Existing, keep
├── index.md                  # Update to reflect new structure
├── characters/               # Existing, keep
│   └── *.md
├── world/                    # Existing, keep
│   └── story-bible.md        # Migrated from bible/story-bible.md
│   └── world-rules.md        # Migrated from bible/world-rules.md
├── acts/
│   ├── act-1-outline.md      # Level 3 output
│   ├── act-1/
│   │   ├── ch1-outline.md    # Level 4 output
│   │   ├── ch1/
│   │   │   ├── sc1-draft.md  # Level 5 output
│   │   │   └── sc2-draft.md
│   │   └── ch2-outline.md
│   ├── act-2-outline.md
│   └── act-2/
│       └── ...
└── style-samples/            # Existing, keep
```

#### [NEW] [relationships.yaml](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/canon/relationships.yaml)
YAML entity-relationship tracker with **formalized semantics** (C3):
- Entity registry with type, introduction point, **aliases**, stable entity IDs
- **Controlled relationship vocabulary** (no free-form rel strings)
- **Temporal fields**: `valid_from`, `valid_to` (null = still active)
- **Supersession chain**: `supersedes`, `superseded_by`
- **Confidence + source**: confidence level + artifact line pointer
- Queryable via grep or Python helper

```yaml
# Controlled vocabulary
rel_vocabulary:
  positive: [trusts, loves, respects, allies_with, protects, depends_on]
  negative: [distrusts, fears, hates, suspects, resents]
  neutral: [knows, employs, related_to, located_at, possesses]
  causal: [caused, prevented, enabled, discovered]

entities:
  marcus:
    type: character
    aliases: ["Marcus", "Reeves", "the soldier", "the man with the prosthetic"]
    introduced: L1/concept

relationships:
  - id: rel_001
    from: marcus
    to: elena
    rel: distrusts              # MUST be from vocabulary
    context: "refuses her help at Zone perimeter"
    valid_from: Act1/Ch1
    valid_to: null               # null = still active
    confidence: high
    source: "canon/acts/act-1/ch1-outline.md#L23"
    supersedes: null
    superseded_by: null
```

#### [DELETE] [Entity-relationship-matrix.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/canon/Entity-relationship-matrix.md)
Replaced by `relationships.yaml`. The LOTR example will be preserved as a comment/test fixture.

---

### Pipeline State

#### [NEW] [.pipeline-state.yaml](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/.pipeline-state.yaml)
Machine-readable state + context manifest:
- `position:` (level, act, chapter, scene)
- `mode:` (manual / mob)
- `canon_version:` (integer, incremented on each commit) + `last_commit_hash:` (C2)
- `context_manifest:` (exactly which files to load for next step)
- `agents:` (which agents are active + model tiers + prompt versions)
- `nodes:` (status of each node in the grid: pending/in_progress/complete/stale)
- `mob_config:` max rounds, budget cap, diminishing return threshold (C5)
- `reproducibility:` context manifest hash, canon version, agent config snapshot (M1)

---

### Support Scripts

#### [NEW] [scripts/context_loader.py](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/context_loader.py)
Reads `.pipeline-state.yaml`, generates the context manifest based on deterministic rules (parent chain, sibling, references), outputs file list for the CLI to load.

#### [NEW] [scripts/start_step.bat](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/start_step.bat) + [start_step.sh](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/start_step.sh)
Zero-friction session handoff wrapper. Reads `.pipeline-state.yaml`, calls `context_loader.py` to get file list, starts a fresh Claude Code CLI session with context pre-loaded. User types `start_step` and they're in — no manual file hunting. Supports `--continue` flag for soft context reset within the same session (for quick steps under 5 minutes).

#### [NEW] [scripts/relationship_query.py](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/relationship_query.py)
Query helper for `relationships.yaml`:
- `query(entity, as_of, status)` → returns matching relationships (searches all aliases)
- `add(from, to, rel, context, established)` → appends entry, **validates rel term against vocabulary** (C3)
- `render_matrix(as_of)` → generates human-readable markdown matrix view
- `--validate` → strict schema gate: unknown rel terms → reject, missing temporal fields → reject, broken supersession chain → warn

#### [NEW] [scripts/migrate_bible_to_canon.py](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/migrate_bible_to_canon.py)
One-shot migration script (M3) with:
- `--dry-run` → shows mapping report without moving files
- `--execute` → moves files, updates refs in all skills
- `--rollback` → reverts from rollback file
- `--verify` → integrity post-check (all refs resolve, no orphans)

#### [MODIFY] [scripts/validate_coauthor_setup.py](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/validate_coauthor_setup.py)
Update to validate new `canon/` structure including `relationships.yaml` schema, `acts/` hierarchy, and `.pipeline-state.yaml`.

---

### Bible Migration

#### [MODIFY] [bible/](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/bible)
Migrate contents to `canon/`:
- `story-bible.md` → `canon/world/story-bible.md`
- `world-rules.md` → `canon/world/world-rules.md`
- `scene-tracker.md` → `canon/timeline.md` (merge with existing stub)
- Keep `bible/` as symlinks or redirect file for backward compatibility

---

### Skills Path Update

#### [MODIFY] All 12 skills in `.claude/skills/*/SKILL.md`
Update file path references from `bible/` to `canon/` paths. Update inputs to reference `relationships.yaml` where continuity context is needed.

---

## Phase 1: New Skills (Levels 1-3)

### New Skills

#### [NEW] [.claude/skills/story-concept/SKILL.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/.claude/skills/story-concept/SKILL.md)
- **Input**: Genre, protagonist sketch, inciting situation, world premise, comparable titles
- **Output**: Structured 1-pager → written to `canon/story-concept.md`
- **Incorporates**: `story-promise` skill output (central question, stakes)
- **Level**: 1

#### [NEW] [.claude/skills/story-arc-builder/SKILL.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/.claude/skills/story-arc-builder/SKILL.md)
- **Input**: Story concept (Level 1 output), character profiles, genre conventions
- **Output**: Act structure + character arc trajectories + thematic pressure points + subplot map → written to `canon/story-arc.md`
- **Level**: 2

#### [NEW] [.claude/skills/act-outline/SKILL.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/.claude/skills/act-outline/SKILL.md)
- **Input**: Story arc (Level 2 output), act number, character arcs
- **Output**: Ordered chapter list with titles, beat descriptions, character arc positions, subplot threads → written to `canon/acts/act-N-outline.md`
- **Level**: 3

### New Templates

#### [NEW] [templates/story-concept.template.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/templates/story-concept.template.md)
#### [NEW] [templates/story-arc.template.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/templates/story-arc.template.md)
#### [NEW] [templates/act-outline.template.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/templates/act-outline.template.md)

---

## Phase 2A: Simulated MOE (MVP)

Single Claude Code session where the Lead Editor role-switches through agents. Accepts some context pollution between agent roles but gets the protocol working fast and generates trace data.

#### [NEW] [agents/](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/agents)
Agent role definition files:

```
agents/
├── lead-editor.md          # Orchestration, formatting, turn management
├── plot-analyst.md         # Structure, causality, tension, Story Grid
├── character-specialist.md # Psychology, voice, motivation, arc integrity
├── depth-partner.md        # Theme, philosophy, meaning pressure
├── continuity-agent.md     # Entity search, fact cross-reference (sidecar)
└── prose-crafter.md        # Line-level quality (active at L4-L5 only)
```

Each file contains the agent's system prompt, model tier, active levels, and behavioral rules (cite files not conversation, one comment at a time, etc.).

In Phase 2A, the Lead Editor loads all agent definitions and role-switches: "Now speaking as Plot Analyst..." → comment → human responds → "Now speaking as Character Specialist..." etc. This runs in a single Claude session with no external orchestrator.

## Phase 2B: Real Orchestrator (When Evals Justify)

Build only when Phase 2A eval data shows cross-agent context pollution is degrading quality.

#### [NEW] [scripts/mob_orchestrator.py](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/mob_orchestrator.py)
Python CLI tool that:
1. Reads `.pipeline-state.yaml` manifest
2. Loads context files per manifest
3. Phase 1: Calls Lead Editor (separate API call) to structure human input
4. Phase 2: Calls each active agent (separate API call per agent, separate context), presents comments to human in terminal
5. Phase 3: Asks "another round, move on, or jump?"
6. Phase 4: Validates `commit_patch` against schema → proposes patch → validates against latest canon + continuity → commits with `canon_version` bump (C2: optimistic locking)
7. Supports Mode A (skip agents, validate only) and Mode C (full mob)
8. **Enforces citation rule** (M5): only canon/artifact-cited claims can mutate canon; uncited claims tagged `[advisory]`

### Mob Termination Governance (C5)

Stop conditions enforced by the orchestrator (both Phase 2A and 2B):

| Condition | Default | Action |
|-----------|---------|--------|
| Max rounds reached | 3 | Prompt: "commit, park, or override?" |
| Budget cap exceeded | $1.00/node | Hard stop, must commit or park |
| Diminishing returns | 0 accepted deltas in round | Prompt: "no changes accepted, ready to commit?" |
| Time cap (optional) | none | User-configurable |

Configurable per node via `mob_config` in `.pipeline-state.yaml`.

---

## Phase 3: Continuity Agent Sidecar

#### [NEW] [scripts/continuity_check.py](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/continuity_check.py)
Standalone script invoked by the orchestrator (or manually):
1. Receives current artifact text
2. **LLM-assisted entity extraction** (cheap Haiku call): resolves pronouns, nicknames, and oblique references to entity names ("the man with the prosthetic" → `marcus`)
3. Queries `relationships.yaml` for all active relationships involving those entities, **searching all aliases**
4. Compares artifact claims against YAML facts
5. Returns `continuity_report` **validated against schema** (C1)
6. On step commit: updates `relationships.yaml` with new/changed relationships + any new aliases discovered

Trigger rules (M4 — two-tier checking):

| Trigger | Check Level | Cost |
|---------|-------------|------|
| **Any commit** (human or AI) | Lightweight auto-check: entity extraction + relationship lookup only | ~$0.001 |
| **AI changes** | Full deep-check: lightweight + semantic comparison + timeline validation | ~$0.01 |
| **Human request** | Full deep-check (same as AI) | ~$0.01 |

---

## Phase 4: Pipeline Integration

#### [MODIFY] [.claude/commands/pipeline-run.md](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/.claude/commands/pipeline-run.md)
Add Stage 0 (Story Development) before existing Stage 1:

```
Stage 0: Story Development (NEW)
  Step 0A: story-concept → canon/story-concept.md
  Step 0B: story-arc-builder → canon/story-arc.md
  Step 0C: act-outline → canon/acts/act-N-outline.md (per act)
  PAUSE: Human review

Stage 1: Chapter Planning (existing)
Stage 2: Drafting (existing)
Stage 3: Revision (existing)
```

#### Navigation
Grid-based navigation via the orchestrator:
- "next step" (deeper), "next sibling" (horizontal), "go up", "jump to"
- Manifest auto-generated at each navigation point
- Cascade warnings when revising upstream nodes

#### Session Boundaries
- New conversation per step (recommended) — use `start_step` wrapper for zero-friction handoff
- `--continue` flag for soft reset within same session (quick steps)
- Manifest file provides complete handoff
- Decision log captures rationale (not deliberation)

#### Git Integration
- **Mandatory `git commit` at every step completion** (Phase 4: Commit)
- Commit message format: `pipeline: {step_name} complete`
- Git tag: `step/{step_name}` (e.g., `step/act2-outline`)
- Decision log records commit hash for each step
- **Undo = `git checkout step/{name} -- canon/ .pipeline-state.yaml`** — named restore points for any step

---

## Cross-Cutting: Tracing & Evals

Built into every phase from the start, not bolted on later.

### Trace Output Format (M2: Dual-Write)

Every agent call produces a trace in **two formats**:
- `.trace.json` — machine source-of-truth (all structured data, scores, costs, reproducibility bundle)
- `.trace.md` — human-readable rendered view (generated from JSON, editable for explicit HUMAN-EVAL annotations)

#### [NEW] [traces/](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/traces)

```
traces/
├── 2026-02-10_act1-outline_mob-round1.trace.json  # machine source
├── 2026-02-10_act1-outline_mob-round1.trace.md    # human view
├── 2026-02-10_act1-outline_continuity.trace.json
├── 2026-02-10_act1-outline_continuity.trace.md
└── ...
```

Each trace file:

```markdown
# Trace: Act 1 Outline — MOE Mob Round 1

**Timestamp**: 2026-02-10T16:30:00Z
**Step**: L3/Act1  |  **Mode**: mob
**Model config**: all agents on claude-haiku

## Context Loaded
- canon/story-concept.md (1,204 tokens)
- canon/story-arc.md (2,891 tokens)
- canon/characters/marcus.md (847 tokens)
- Total context: 6,142 tokens

## Phase 1: Structure
**Human input**: (raw text shown here)
**Lead Editor output**: (structured version shown here)
**Human accepted**: yes / adjusted: (what changed)

## Phase 2: Comments

### Plot Analyst (claude-haiku)
**Comment**: "Ch3 feels like a stall — no value shift..."
**Human response**: "Good catch. Changed to..."
**Resolution**: accepted
<!-- HUMAN-EVAL: comment-quality=4/5, relevance=5/5 -->
<!-- HUMAN-EVAL: model-adequate=yes -->

### Character Specialist (claude-haiku)
**Comment**: "Marcus's reaction in Ch2 feels generic..."
**Human response**: "Disagree, his military background..."
**Resolution**: rejected
<!-- HUMAN-EVAL: comment-quality=2/5, relevance=3/5 -->
<!-- HUMAN-EVAL: model-adequate=no, reason="shallow character reasoning" -->

### Depth Partner (claude-haiku)
**Comment**: "The prosthetic metaphor could..."
**Human response**: ...
**Resolution**: ...
<!-- HUMAN-EVAL: comment-quality=___/5, relevance=___/5 -->
<!-- HUMAN-EVAL: model-adequate=___, reason="" -->

## Artifact Committed
**File**: canon/acts/act-1-outline.md
**Relationships updated**: 3 new, 0 changed

## Cost
| Agent | Model | Input tokens | Output tokens | Cost |
|-------|-------|-------------|--------------|------|
| Lead Editor | claude-haiku | 6,200 | 1,100 | $0.002 |
| Plot Analyst | claude-haiku | 6,500 | 450 | $0.001 |
| ... | ... | ... | ... | ... |
| **Total** | | | | **$0.008** |
```

### Eval Scoring: Implicit by Default, Explicit Optional

**Primary method — implicit signals** (auto-captured, zero writer effort):

| Human Action During Mob | Auto-Score | Rationale |
|------------------------|------------|----------|
| Accepts comment without edit | quality=5, relevance=5 | Full agreement |
| Accepts with minor edits | quality=4, relevance=4 | Good direction, refined |
| Back-and-forth then accepts | quality=3, relevance=4 | Needed discussion but relevant |
| Rejects comment | quality=1, relevance=2 | Not useful |
| Skips without responding | quality=2, relevance=1 | Not worth engaging |

The orchestrator captures these signals automatically from the conversation flow. **No forms, no annotation, no extra work.**

**Secondary method — explicit annotation** (optional, for when the writer wants to leave specific feedback):

`<!-- HUMAN-EVAL: ... -->` templates remain in trace files for the rare case (~1 in 10) when the human wants to explain WHY something was wrong (e.g., "technically correct but missed the tone," or "this agent needs a model upgrade for this type of task"). These are valuable but not required.

### Eval Dimensions

| Dimension | Source | Scale | What It Measures |
|-----------|--------|-------|------------------|
| `comment-quality` | Implicit | 1-5 | Was the comment insightful? |
| `relevance` | Implicit | 1-5 | Was it about something that matters? |
| `model-adequate` | Derived | yes/no | Derived from patterns: >60% rejection over 5 traces = no |
| `structure-quality` | Implicit | 1-5 | Phase 1 accept/adjust/rewrite signal |
| `continuity-accuracy` | Implicit | 1-5 | False positive/negative rate in continuity reports |
| `session-cost` | Auto | $ | Total cost of this step |

### Model Upgrade Decision Rule

```
IF agent's average comment-quality < 3.0 over last 5 traces
   AND rejection rate > 60% over same period
   THEN recommend upgrade that agent's model one tier
   AND re-run same step to compare
```

All data comes from implicit signals. No writer effort required for the eval loop to function.

### LLM-as-Judge (Future)

After ~20-30 traces with implicit scores exist, add:

#### [NEW] [scripts/eval_judge.py](file:///c:/Users/david/OneDrive/G-drive/K-D/Claude-Writing-Skills/scripts/eval_judge.py)
- Reads a trace `.md` file
- Sends each agent comment + human response + resolution to a judge model
- Judge scores `comment-quality` and `relevance` using implicit scores as calibration baseline
- Can detect subtler patterns: "agent gave good craft advice but ignored the genre conventions"
- Once calibrated (>80% agreement with implicit scores), can auto-flag model-inadequacy

---

## User Review Required

> [!IMPORTANT]
> **Phase ordering**: Phases 0-1 can be built independently. Phase 2 (orchestrator) depends on Phase 0 (manifest format). Phase 3 (continuity) depends on Phase 0 (YAML relationships). Phase 4 integrates everything. Recommend building Phase 0 → Phase 1 → Phase 2+3 in parallel → Phase 4.

> [!WARNING]
> **Breaking change**: Migrating `bible/` to `canon/` will break any existing workflows that reference `bible/` paths. Backward-compatible redirects are included in the plan but any running projects should be migrated carefully.

## Verification Plan

### Automated Tests

1. **YAML schema validation**: `python scripts/relationship_query.py --validate`
2. **Context manifest generation**: `python scripts/context_loader.py --test`
3. **Continuity check**: `python scripts/continuity_check.py --test` — against sample with known violations
4. **Setup validation**: `python scripts/validate_coauthor_setup.py`
5. **Trace generation**: Verify every agent call produces a well-formed `.trace.md` with all sections
6. **Eval aggregation**: `python scripts/eval_judge.py --aggregate traces/` — summary of scores across all traces

### Manual Verification

1. **End-to-end flow**: Create concept (Mode A) → MOE Mob on arcs (Mode C) → navigate to Act 2 in new conversation → verify context loads from manifest
2. **Continuity round-trip**: Add relationship in Act 1, write conflicting artifact in Act 2, verify continuity agent catches it
3. **Mode switching**: Start in Mode C, switch to Mode A mid-step
4. **Trace annotation loop**: Run one mob session → open trace in Antigravity → annotate with HUMAN-EVAL scores → verify annotations parse correctly for aggregation
5. **Model upgrade test**: After annotating 5+ traces for one agent, run upgrade decision rule, verify it recommends upgrade only when `model-adequate=no` pattern is clear

> [!NOTE]
> Traces are generated from Phase 0 onward — even before the orchestrator is built, individual skill runs should produce trace files for eval.
