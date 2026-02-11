---
name: Mob Session
description: Run a simulated MOE review session on the current pipeline artifact with specialist agent role-switching.
---

# Mob Session Skill

Run a simulated Mixture of Experts (MOE) review session where the Lead Editor role-switches through specialist agents to critique and improve the current pipeline artifact.

## Usage
```
/project:skills:mob-session
```

## Process

### Context Loading
Before starting the session, load context via the pipeline state manifest:

1. Read `.pipeline-state.yaml` for current position and manifest.
2. Run `python scripts/context_loader.py` (or read `context_manifest` from pipeline state) to determine which files to load.
3. Load system files: `.pipeline-state.yaml`, `canon/preferences.md`
4. Load parent chain files (determined by current level per context loader rules).
5. Load the current artifact being reviewed.
6. Load agent definitions from `agents/*.md` for all agents active at the current level.

### Agent Activation by Level

| Agent | L1 | L2 | L3 | L4 | L5 |
|-------|----|----|----|----|-----|
| Lead Editor | active | active | active | active | active |
| Plot Analyst | active | active | active | active | off |
| Character Specialist | off | active | active | active | active |
| Depth Partner | active | active | active | off | off |
| Continuity Agent | off | off | active | active | active |
| Prose Crafter | off | off | off | active | active |

### 4-Phase Protocol

Follow the protocol defined in `docs/mob_protocol.md`:

#### Phase 1: Structure Offer
1. Read the current artifact (or receive raw human input for a new artifact).
2. Organize input into the step's template format (using the appropriate template from `templates/`).
3. Present the structured version to the human.
4. Human responds: `accept` / `adjust` / `override` / `skip`

#### Phase 2: Comment Queue
For each active agent at the current level, in sequence:

1. Announce role switch using explicit separators:
   ```
   --- Now speaking as {Agent Name} ---
   ```
2. Present ONE focused comment with canon file citations.
3. Wait for human response: `accept` / `reject` / `revise` / `park`
4. If not resolved, allow up to 2 back-and-forth exchanges.
5. Announce end of agent turn:
   ```
   --- End {Agent Name} ---
   ```
6. Move to next agent.

Agent sequence: `Plot Analyst → Character Specialist → Depth Partner → Continuity Agent → Prose Crafter`
(Skip agents inactive at current level.)

#### Phase 3: Resolution Check
1. Summarize accepted deltas and parked questions in a round ledger:
   ```markdown
   ## Round {N} Ledger
   | Agent | Comment Summary | Resolution | Citations |
   |-------|----------------|------------|-----------|
   ```
2. Check governance rules (see `docs/mob_protocol.md#Governance`):
   - If round count >= `mob_config.max_rounds` → prompt: "Round limit reached. Commit, park, or override?"
   - If 0 accepted deltas this round → prompt: "No changes accepted. Ready to commit?"
3. Ask: "Another round, commit, or park?"

#### Phase 4: Commit
1. Write the canonical artifact to the correct file path.
2. Update `canon/relationships.yaml` with any new/changed relationships (with source citations).
3. Advance `.pipeline-state.yaml` position per the standard state advancement rules:
   - L1 artifact → `level: L2`
   - L2 artifact → `level: L3, act: null`
   - L3 artifact (act N) → `level: L3, act: N`
4. Output a trace record summarizing the session (for later rendering via `scripts/trace_renderer.py`).

### Governance Rules
- **Max rounds**: Read from `.pipeline-state.yaml` `mob_config.max_rounds` (default: 3).
- **Diminishing returns**: If `mob_config.diminishing_return_threshold` accepted deltas or fewer in a round, prompt to commit.
- **Citation enforcement**: Comments without `canon/` file citations are tagged `[advisory]` and cannot drive canon changes without human override. See `docs/citation_enforcement.md`.
- **Budget cap**: Not enforced in Phase 2A (single-session role-switching cannot track per-agent costs). Active in Phase 2B.

## Output Format
The mob session does not produce a single output file — it modifies the current artifact in place and optionally updates `canon/relationships.yaml`. The session's decisions are captured in a trace record.

## Quality Checks
- All 4 phases were executed in order.
- Role-switch separators were used for each agent.
- Each agent commented only within their defined scope.
- All cited comments reference actual `canon/` file paths.
- Advisory comments were tagged appropriately.
- Round ledger was maintained.
- Governance rules were checked at Phase 3.
