# Response to Second Architecture Review

## Overall: AGREE with the framing

The reviewer correctly identifies this as an **upgrade path, not a pivot**. The state-machine + contract-first refinement is exactly what separates a design document from a buildable system. Most of these findings catch gaps in formalization that would have bitten us during implementation.

Let me go through each one. I'll flag overlaps with the first review and focus on unique points.

---

## Critical Findings

### C1: Missing Hard Contracts — AGREE, THIS IS THE BIGGEST GAP

**This is the most important finding in either review.** We defined roles, phases, and data flows, but never specified *what the data looks like* at each boundary. Without schemas:

- The Lead Editor outputs free-form text that the orchestrator can't validate
- The continuity agent returns a "report" with no guaranteed structure
- Trace files have implied sections that nothing enforces

**Accept the fix fully.** Define JSON/YAML schemas for:

| Contract | Validates | When |
|----------|-----------|------|
| `node_input` | What context + instructions go into each skill/agent call | Before agent call |
| `agent_comment` | Agent output structure (comment text, citations, suggested changes) | After agent responds |
| `continuity_report` | Passes/flags/violations with entity refs and evidence | After continuity check |
| `commit_patch` | What changes to canon, what relationships added/changed | Before step commit |
| `trace_record` | Complete session record with all required sections | After session |

**Implementation timing**: Phase 0. Define schemas before building anything. Every script validates against schemas.

---

### C2: Canon Write Concurrency — AGREE FOR PHASE 2B, LOW RISK FOR PHASE 2A

For **Phase 2A** (single session, role-switching): there's only one writer (the current Claude session). No race conditions possible. This is a non-issue for MVP.

For **Phase 2B** (real orchestrator with parallel API calls): the reviewer is correct. If the Plot Analyst and Character Specialist both suggest changes to `act-1-outline.md`, we need transaction semantics.

**Accept the fix, but scope it to Phase 2B:**

```yaml
# In .pipeline-state.yaml
canon_version: 47
last_commit_hash: "a3f2c1d"
```

The 3-step commit protocol (propose → validate → commit with version bump) is the right approach. Abort/rebase on version mismatch.

**Implementation timing**: Phase 2B. For Phase 2A, the single-session model provides serialization for free.

---

### C3: Relationship YAML Semantics Unbounded — AGREE, IMPORTANT

We defined the YAML format but left the *semantics* informal. Without controlled vocabulary:

- One session writes `rel: distrusts`, another writes `rel: suspicious_of`, another writes `rel: doesn't_trust`. Same meaning, three different strings.
- No way to query "all negative relationships" because the vocabulary is unbounded.
- Temporal validity is implicit in `established` but there's no `valid_to` for ended relationships, and no supersession chain.

**Accept the fix fully.** Add:

```yaml
# Schema enforcement
rel_vocabulary:
  positive: [trusts, loves, respects, allies_with, protects, depends_on]
  negative: [distrusts, fears, hates, suspects, resents]
  neutral: [knows, employs, related_to, located_at, possesses]
  causal: [caused, prevented, enabled, discovered]

relationships:
  - id: rel_042                    # stable ID
    from: marcus
    to: elena
    rel: distrusts                 # MUST be from vocabulary
    context: "refuses her help at Zone perimeter"
    valid_from: Act1/Ch1           # temporal validity
    valid_to: null                 # null = still active
    confidence: high               # high/medium/low
    source: "canon/acts/act-1/ch1-outline.md#L23"  # artifact line
    supersedes: null               # chain to prior relationship
    superseded_by: null
```

The `--validate` script becomes a strict gate: unknown rel terms → rejected, missing temporal fields → rejected, broken supersession chain → warning.

**Implementation timing**: Phase 0, as part of the relationships.yaml schema definition.

---

### C4: Model Routing May Underfit — PARTIALLY AGREE

**Overlap with first review**: the "start cheap" strategy was already discussed. This review adds a useful nuance: **complexity-triggered floors**.

**Where I agree**: The Depth Partner reasoning about thematic arcs at L2 genuinely needs stronger model priors. Running it on Haiku for the first 10 sessions just to "establish a baseline" risks polluting the arc structure that everything downstream depends on.

**Where I'm cautious**: Automatic complexity detection ("high thematic density or many entities") requires a pre-analysis step that itself costs tokens. The complexity guard could become more expensive than just using Sonnet.

**Accepted fix — simplified version:**

```
Rule: 
  IF level <= L3 (story concept, arcs, act outlines)
    THEN floor = Sonnet for Depth Partner and Character Specialist
    ELSE default = Haiku (upgradable via evals)
```

Rationale: L1-L3 artifacts are **load-bearing** — everything downstream depends on them. Saving $0.05 on a Haiku call at L2 isn't worth corrupting the arc structure. At L4-L5 (chapter outlines, scene drafts), cheap models are fine because the damage radius is one scene.

**Implementation timing**: Phase 0 (model config), refined by Phase 2A eval data.

---

### C5: MOE Mob Lacks Termination Governance — AGREE

**This is correct and I should have caught it.** "Another round, move on, or jump?" without stop conditions means:

- A perfectionist writer does 12 rounds on Act 1 Chapter 1 and burns $5 in tokens
- The agents keep finding new things to say because they have no diminishing-return awareness
- Decision fatigue sets in and the writer accepts bad suggestions just to move on

**Accept the fix fully:**

```yaml
# In .pipeline-state.yaml per node
mob_config:
  max_rounds: 3                    # hard cap
  budget_cap_usd: 1.00             # per node
  diminishing_return_threshold: 0  # if 0 new accepted deltas in a round, auto-prompt commit
  mandatory_decision_after: 3      # "commit or park" after N rounds
```

After `max_rounds` or `budget_cap`: orchestrator says "Budget/round limit reached. Commit current state, park for later, or override limit?"

**Diminishing return detection**: If a full round produces zero accepted changes, the orchestrator prompts: "No changes accepted this round. Ready to commit?"

**Implementation timing**: Phase 2A (even in simulated MOE, the Lead Editor can enforce round counting).

---

## Medium Findings

### M1: Reproducibility Bundle — AGREE

**Not a duplicate.** The first review discussed session handoff friction; this review discusses session handoff *integrity*. Different problems.

Without a reproducibility bundle, you can't debug why a Tuesday session produced bad output — you don't know what context it loaded, which model versions were used, or what the canon looked like at that moment.

**Accepted fix:**

```yaml
# Stored in each trace record AND in .pipeline-state.yaml
reproducibility:
  context_manifest_hash: "sha256:a3f2..."     # hash of loaded files
  canon_version: 47
  agent_config:
    lead_editor: {model: claude-haiku, provider: claude, prompt_version: "1.2"}
    plot_analyst: {model: claude-haiku, provider: claude, prompt_version: "1.0"}
  pipeline_state_hash: "sha256:b4c1..."
  timestamp: "2026-02-10T16:30:00Z"
```

**Implementation timing**: Phase 0 (schema), implemented in trace generation.

---

### M2: Dual-Write Traces — AGREE, SMART

**Markdown for humans, JSON for machines.** We already hit this problem conceptually — the implicit eval scoring system needs to parse trace files programmatically, and parsing markdown with regex is the canonical "now you have two problems" scenario.

**Accepted fix:**

```
traces/
├── 2026-02-10_act1-outline_round1.trace.md    # human-readable (generated from JSON)
├── 2026-02-10_act1-outline_round1.trace.json  # machine source-of-truth
```

The JSON contains all structured data (scores, costs, agent configs, reproducibility bundle). The markdown is a **rendered view** of the JSON, generated by a template. Edit the JSON → regenerate the markdown. Or: for the rare explicit HUMAN-EVAL annotations, the human edits the markdown and a parser extracts the annotation back into the JSON.

**Implementation timing**: Phase 0 (schema for trace JSON), built into orchestrator.

---

### M3: Migration Tooling — AGREE (OVERLAP, BUT NEW DETAIL)

The first review noted the breaking change. This review adds the specific fix: a one-shot migration script with dry-run, rollback file, integrity post-check.

**Accepted fix:**

```bash
# scripts/migrate_bible_to_canon.py
python scripts/migrate_bible_to_canon.py --dry-run    # shows mapping report
python scripts/migrate_bible_to_canon.py --execute     # moves files, updates refs
python scripts/migrate_bible_to_canon.py --rollback    # reverts from rollback file
python scripts/migrate_bible_to_canon.py --verify      # integrity post-check
```

**Implementation timing**: Phase 0, before any other changes.

---

### M4: Continuity Trigger Asymmetry — AGREE, GOOD REFINEMENT

**Unique point.** Our rule was: auto on AI changes, manual on human changes. The reviewer correctly notes that humans can introduce contradictions too — especially during rapid editing where they forget what they established 10 chapters ago.

**Accepted fix — two-tier checking:**

| Trigger | Check Level | What It Does |
|---------|-------------|-------------|
| Any commit (human or AI) | **Lightweight auto-check** | Entity extraction + relationship lookup only. No deep reasoning. ~$0.001. Flags obvious contradictions. |
| AI changes | **Full deep-check** | Lightweight + semantic comparison + timeline validation. ~$0.01. |
| Human request | **Full deep-check** | Same as AI changes. On-demand. |

The lightweight check catches "Marcus is described as having two working legs in a scene where his prosthetic should be mentioned." It doesn't catch subtle thematic contradictions — that's what the full check is for.

**Implementation timing**: Phase 3.

---

### M5: Citation Enforcement — AGREE, IMPORTANT BOUNDARY RULE

**Unique and important.** This operationalizes "conversation = scratch paper, files = memory" as a hard rule rather than a guideline.

**Accepted fix:**

```
RULE: Only claims with canon/artifact citations can mutate canon.

If an agent says: "Marcus should distrust Elena because of their history"
  → This is ADVISORY. Cannot be committed to relationships.yaml.

If an agent says: "Per canon/characters/marcus.md#L15, Marcus has military 
  background. This conflicts with the nurturing behavior in act-1/ch3-outline.md#L42"
  → This is CITED. Can be acted on and committed.

Any uncited claim in the decision log is tagged: [advisory, uncited]
Any cited claim is tagged: [cited, source: <file>#L<line>]
```

The commit step validates: does every canon mutation have a citation chain? If not, warn (don't block — the human may override).

**Implementation timing**: Phase 2A (as a rule in the Lead Editor's system prompt), enforced programmatically in Phase 2B.
