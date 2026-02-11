# MOE Mob Protocol

Canonical turn-by-turn rules for simulated Mixture of Experts (MOE) mob sessions. This document supersedes the relevant protocol sections in `docs/human_in_the_loop_design.md` and `docs/context_continuity_models.md`.

## Overview

A mob session is a structured review where the Lead Editor orchestrates specialist agents to critique and improve a pipeline artifact. In Phase 2A (simulated MOE), this runs in a single Claude Code session with role-switching. In Phase 2B, each agent will be a separate API call.

## Phase 1: Structure Offer

The Lead Editor's first action is always to organize the human's input:

> **Lead Editor**: "Here's how I've organized your input into [template] format. Want me to adjust anything before we start the review?"

Human options:
- **Accept**: "Looks good, start comments"
- **Adjust**: "Move X under Y, and add Z"
- **Override**: "I'll write it myself, just comment when I'm done"
- **Skip**: "Already structured, go straight to comments"

If the human provides no raw input (reviewing an existing artifact), Phase 1 presents the current artifact state and asks if the human wants to restructure before review.

## Phase 2: Comment Queue

### Turn Order
Agents speak in a fixed sequence per round:
1. Plot Analyst (structure, causality, tension)
2. Character Specialist (motivation, voice, arc integrity)
3. Depth Partner (theme, moral pressure, meaning)
4. Continuity Agent (facts, timeline, relationships)
5. Prose Crafter (line-level craft — L4/L5 only)

Agents inactive at the current level are skipped.

### Role-Switch Separators
The Lead Editor announces each agent with explicit separators to prevent persona bleed:

```
--- Now speaking as Plot Analyst ---

Act 2A currently has no pinch point between the midpoint and the second plot point. Per `canon/story-arc.md#Act Progression`, the act structure shows a gap in escalation pressure.

--- End Plot Analyst ---
```

### Single-Comment Discipline
Each agent raises exactly ONE comment per turn — their most impactful observation. Additional observations wait for subsequent rounds.

### Human Resolution
After each comment, the human responds:
- **Accept**: Change is applied. Lead Editor updates the artifact.
- **Reject**: No change. Agent's observation is noted in the ledger.
- **Revise**: Human provides modification to the suggestion. Lead Editor applies revised version.
- **Park**: Valid observation but not for now. Recorded for future reference.

If not immediately resolved, up to 2 back-and-forth exchanges are allowed before the Lead Editor moves to the next agent.

## Phase 3: Resolution Check

After all active agents have spoken, the Lead Editor produces a round ledger:

```markdown
## Round {N} Ledger
| Agent | Comment Summary | Resolution | Citations |
|-------|----------------|------------|-----------|
| Plot Analyst | Act 2A needs pinch point | accepted | canon/story-arc.md#L45 |
| Character Specialist | Marcus reaction is generic | rejected | — |
| Depth Partner | Theme underdeveloped in Act 1 | parked | canon/story-concept.md#L23 |
```

### Governance Checks
Before asking the human about the next step, the Lead Editor checks:

1. **Round limit**: If round count >= `mob_config.max_rounds` (default: 3), prompt: "Round limit reached. Commit current state, park remaining items, or override limit?"
2. **Diminishing returns**: If accepted deltas in this round <= `mob_config.diminishing_return_threshold` (default: 0), prompt: "No changes accepted this round. Ready to commit?"

If neither condition triggers, ask: "Another round, commit, or park?"

## Phase 4: Commit

1. **Write artifact**: Save the final version of the artifact to its canonical path.
2. **Update relationships**: Add/modify entries in `canon/relationships.yaml` with source citations pointing to the committed artifact.
3. **Log trace**: Record the session decisions for later rendering via `scripts/trace_renderer.py`.
4. **Advance state**: Update `.pipeline-state.yaml` position per standard rules.

## Citation Enforcement

See `docs/citation_enforcement.md` for full rules. Summary:
- Comments with `canon/` file citations → `cited` → can drive canon changes
- Comments without citations → `advisory` → cannot mutate canon without human override
- The Lead Editor checks citation status before applying any change in Phase 4

## Context Rules

- Agents cite files, not conversation history
- The conversation is scratch paper; canonical files are memory
- At commit, only file-persisted changes survive to the next session
- Context loading follows `scripts/context_loader.py` manifest rules
