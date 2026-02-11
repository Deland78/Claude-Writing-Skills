# Phase 2A Failure Modes Trace

Demonstrates governance mechanisms triggering correctly during mob sessions.

---

## Scenario 1: Advisory Tagging (Uncited Comment)

A depth_partner comment with no canon citations is correctly tagged `[advisory]` and blocked from driving canon changes.

### Round 1 Ledger (excerpt)

| Agent | Comment Summary | Resolution | Citations | Status |
|-------|----------------|------------|-----------|--------|
| plot_analyst | Act 2A needs a pinch point | accepted | canon/story-arc.md#L45 | cited |
| depth_partner | Theme feels underdeveloped in Act 1 | parked | — | advisory |

### What happened

```
--- Now speaking as Depth Partner ---

The thematic pressure feels thin in Act 1. The protagonist doesn't face any
meaningful moral choices until Act 2, which weakens the thematic setup.

--- End Depth Partner ---
```

**Lead Editor**: This comment has no canon file citations. Tagging as `[advisory]`.

> Advisory comments cannot drive canon changes without human override.
> Options: (1) Provide a citation to promote to [cited], (2) Override: "Apply without citation", (3) Park for later.

**Human**: Park for later.

**Result**: Comment recorded in ledger as `advisory, parked`. No canon mutation occurred.

---

## Scenario 2: Max-Round Termination

A session reaches `mob_config.max_rounds` (default: 3) and triggers the termination prompt.

### Round 3 Ledger

| Agent | Comment Summary | Resolution | Citations | Status |
|-------|----------------|------------|-----------|--------|
| plot_analyst | Minor pacing issue in Ch3 transition | accepted | canon/acts/act-1-outline.md#L34 | cited |
| character_specialist | Elena's voice shift needs motivation | rejected | canon/characters/elena.md#L8 | cited |
| continuity_agent | Timeline gap between Ch2-Ch3 | accepted | canon/timeline.md#L15 | cited |

### What happened

**Lead Editor**: Round 3 complete. Governance check: round count (3) >= max_rounds (3).

> **Round limit reached.** 3 rounds completed (max_rounds: 3).
> Options: (1) Commit current state, (2) Park remaining items, (3) Override limit (+1 round).

**Human**: Commit current state.

**Result**: Session proceeded to Phase 4 (Commit). Accepted changes were written to canon. Remaining observations were recorded in the trace but not acted upon.

---

## Scenario 3: Diminishing Returns (Zero Accepted Deltas)

A round where the human rejects or parks all agent comments triggers early termination.

### Round 2 Ledger

| Agent | Comment Summary | Resolution | Citations | Status |
|-------|----------------|------------|-----------|--------|
| plot_analyst | Suggests reordering Ch4 and Ch5 | rejected | canon/acts/act-2-outline.md#L20 | cited |
| character_specialist | Marcus voice too formal in Ch4 | parked | canon/characters/marcus.md#L22 | cited |
| depth_partner | Thematic echo could strengthen Ch3 | parked | canon/story-concept.md#L10 | cited |

### What happened

**Lead Editor**: Round 2 complete. Governance check: accepted deltas this round = 0, threshold = 0.

> **No changes accepted this round.** Diminishing returns detected.
> Options: (1) Commit current state (with Round 1 changes), (2) Park everything, (3) Override and continue.

**Human**: Commit current state.

**Result**: Session committed the changes from Round 1. Round 2 observations were recorded in the trace as rejected/parked. Session ended cleanly without reaching the max round limit.

---

## Summary

| Governance Mechanism | Trigger Condition | Default Threshold | Demonstrated |
|---------------------|-------------------|-------------------|-------------|
| Advisory tagging | Empty citations array | N/A | Scenario 1 |
| Max-round termination | rounds >= max_rounds | 3 | Scenario 2 |
| Diminishing returns | accepted_deltas <= threshold | 0 | Scenario 3 |
| Budget cap | cost >= budget_cap_usd | $1.00 | Deferred to Phase 2B |
