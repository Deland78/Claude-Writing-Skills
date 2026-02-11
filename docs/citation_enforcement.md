# Citation Enforcement Rules

Rules for determining whether an agent comment can drive canon mutations. Implements architecture review finding M5: "Only claims with canon/artifact citations can mutate canon."

## Citation Status

Every agent comment is assigned a `citation_status` based on its `citations` array:

| `citations` array | `citation_status` | Tag in ledger |
|---|---|---|
| Non-empty (at least one `canon/` path) | `cited` | `[cited, source: <file>#L<line>]` |
| Empty | `advisory` | `[advisory, uncited]` |

The `citation_status` field is part of the `agent_comment` schema (`schemas/agent_comment.schema.yaml`).

## Enforcement Rules

### Cited comments (`citation_status: "cited"`)

- **CAN** drive changes to canon files.
- **CAN** add or modify entries in `canon/relationships.yaml`.
- The Lead Editor verifies that cited files actually exist before committing.
- Citations must follow the `canon/<path>#L<line>` format (line reference optional but encouraged).

### Advisory comments (`citation_status: "advisory"`)

- **CANNOT** mutate canon files without explicit human override.
- Tagged `[advisory]` in the round ledger and trace record.
- The human may still act on advisory comments by:
  1. Adding their own citation to support the claim.
  2. Explicitly overriding with: "Apply this without citation."
- If overridden, the trace records the override: `resolution: "accepted"` with a note that the human bypassed citation requirements.

### Enforcement point

The Lead Editor checks citation status at two points:

1. **Phase 3 (Resolution Check)**: When summarizing the round ledger, the Lead Editor tags each comment's citation status.
2. **Phase 4 (Commit)**: Before writing any change to a canon file, the Lead Editor verifies:
   - The originating comment has `citation_status: "cited"`, OR
   - The human explicitly overrode the citation requirement.

## Decision Ledger Tagging

In the round ledger, each comment row includes its citation status:

```markdown
## Round {N} Ledger
| Agent | Comment Summary | Resolution | Citations | Status |
|-------|----------------|------------|-----------|--------|
| plot_analyst | Act 2A needs pinch point | accepted | canon/story-arc.md#L45 | cited |
| depth_partner | Theme underdeveloped | parked | — | advisory |
```

## Trace Record

The `citation_status` field is persisted in the trace record's `phases.comments` array. The trace renderer displays it in the rendered markdown view.

## Budget Cap (Phase 2B only)

Budget-based termination (`mob_config.budget_cap_usd`) is **not enforced** in Phase 2A. Single-session role-switching cannot track actual per-agent API costs. Round limits and diminishing returns are the active governance mechanisms in Phase 2A. Budget enforcement is deferred to Phase 2B when each agent runs as a separate API call.

## References

- Schema: `schemas/agent_comment.schema.yaml` — `citation_status` field
- Protocol: `docs/mob_protocol.md` — Phase 3 governance checks, Phase 4 commit
- Config: `.pipeline-state.yaml` — `mob_config` section
- Architecture review: M5 finding (canon mutation requires citation chain)
