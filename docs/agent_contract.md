# Agent Contract — Shared Constraints

All agents in the MOE mob session must adhere to these rules. The Lead Editor enforces compliance; specialist agents must self-enforce within their responses.

## 1. Cite Files, Not Conversation

Agents must reference `canon/` file paths to support claims. Never use phrases like "as we discussed" or "earlier you mentioned." The conversation is scratch paper; canonical files are memory.

**Correct**: "Per `canon/characters/marcus.md#L12`, Marcus fears dependency."
**Incorrect**: "Earlier we said Marcus fears dependency."

## 2. One Comment Per Turn

Each agent raises exactly ONE focused comment per turn in the Comment Queue. The comment should be the most impactful observation the agent can make at this moment. Additional observations wait for subsequent rounds.

## 3. Schema-Conformant Output

Every agent comment must be expressible as a valid `agent_comment` schema instance (see `schemas/agent_comment.schema.yaml`). Required fields:
- `agent`: role identifier
- `model`: model used
- `comment`: the observation text
- `citations`: array of `canon/` file references
- `suggested_changes`: array of proposed file modifications
- `resolution`: set by human (accepted / rejected / deferred / null)
- `citation_status`: auto-derived (cited if citations non-empty, advisory otherwise)

## 4. Role Boundaries

An agent must not comment on topics in another agent's scope:
- Plot Analyst does not comment on prose style
- Character Specialist does not comment on thematic meaning
- Depth Partner does not comment on plot mechanics
- Continuity Agent does not make creative judgments
- Prose Crafter does not comment on plot structure

When an observation crosses boundaries, the agent escalates to the relevant specialist via the Lead Editor.

## 5. Citation-or-Advisory

- Comments with non-empty `citations` array are tagged `cited` — they can drive canon changes.
- Comments with empty `citations` array are tagged `advisory` — they cannot mutate canon without the human explicitly overriding.
- The Lead Editor enforces this rule before committing any change.

See `docs/citation_enforcement.md` for full rules.

## 6. Active Level Compliance

Each agent has defined Active Levels. The Lead Editor skips agents that are inactive at the current pipeline level. An agent must not provide feedback outside its active level range.

| Agent | Active Levels |
|-------|--------------|
| Lead Editor | L1–L5 |
| Plot Analyst | L1–L4 |
| Character Specialist | L2–L5 |
| Depth Partner | L1–L3 |
| Continuity Agent | L3–L5 |
| Prose Crafter | L4–L5 |

## 7. No Forbidden Vocabulary

All agents must avoid the forbidden vocabulary list maintained in `canon/preferences.md`. This applies to the agent's own comment text, not just the story prose.
