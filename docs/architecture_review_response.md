# Response to Architecture Review

## Verdict: Agree on all five. One partial.

---

### 1. Friction Accumulation — AGREE, CRITICAL

**The reviewer is right.** I designed "new conversation per step" as the cleanest solution for context pollution but underestimated the UX cost of doing it 50+ times across a novel. The gap between "architecturally clean" and "actually used" is exactly this kind of friction.

**What I'd change:**

Create a wrapper script (`start_step.bat` / `start_step.sh`) that automates the entire handoff:

```bash
#!/bin/bash
# start_step.sh — zero-friction session handoff

# 1. Read current position from pipeline state
MANIFEST=$(python scripts/context_loader.py --output-files)

# 2. Build the context loading prompt
CONTEXT_PROMPT="Load these files and follow the MOE Mob protocol:\n"
for file in $MANIFEST; do
  CONTEXT_PROMPT+="- $file\n"
done

# 3. Start a fresh Claude Code session with context pre-loaded
claude --system-prompt agents/lead-editor.md \
       --load-files $MANIFEST \
       --message "$CONTEXT_PROMPT"
```

The user types `start_step` in the terminal and they're in. No manual file hunting, no copy-pasting manifests, no remembering where they left off. **The session boundary becomes invisible.**

**Additionally**: For steps that are quick (under 5 minutes), the orchestrator should support a `--continue` flag that stays in the same session but does a soft context reset (Lead Editor posts the anchor artifact and says "fresh start, referencing files only"). This is less pure but avoids friction for rapid iteration.

---

### 2. Entity Extraction Fragility — AGREE, CRITICAL

**The reviewer is exactly right.** Grep for "Marcus" catches literal mentions but misses pronouns, nicknames, and oblique references. A scene might never say "Marcus" but describe "the man with the prosthetic" for three paragraphs. The continuity agent would report "Marcus not mentioned" when he's the entire scene.

**What I'd change:**

**a) Entity aliasing in YAML:**

```yaml
entities:
  marcus:
    type: character
    aliases:
      - "Marcus"
      - "the soldier"
      - "the man with the prosthetic"
      - "Reeves"           # surname
    introduced: L1/concept
```

The search script greps for ALL aliases, not just the primary name. Aliases are maintained as part of the entity registry — when a new nickname appears in a draft, it gets added.

**b) LLM-assisted entity extraction before grep:**

Instead of grepping raw text, make a cheap Haiku call first:

```
System: Extract all entity references from this text. 
Include pronouns resolved to their referent, nicknames, 
and oblique descriptions. Return a list of 
(mention, entity_name) pairs.

Input: [draft text]

Output:
- "He" → marcus
- "the man with the prosthetic" → marcus  
- "Zone 2 perimeter" → zone-2
- "her pack" → elena
```

THEN grep `relationships.yaml` for each resolved entity. This bridges semantic understanding and keyword search at minimal cost (~$0.001 per extraction call).

---

### 3. Orchestrator Complexity — PARTIALLY AGREE

**Where I agree:** Building a robust Python orchestrator that manages subprocess I/O, parses streaming text output, handles errors, and coordinates multiple API calls IS a significant engineering effort. It's the riskiest piece to build and the most likely to have bugs.

**Where I partially disagree:** The "Simulated MOE" suggestion (Lead Editor uses a `consult_agent` tool within one Claude session) has a specific problem we already designed around — **context pollution**. If all agents share one context, the Character Specialist's rejected comments bleed into the Plot Analyst's reasoning. The whole point of the sidecar pattern was to avoid this.

**What I'd change — a two-stage approach:**

**MVP (Simulated MOE):** Use a single Claude Code session where the Lead Editor role-switches through agents. Accept the pollution risk for now. This gets the protocol working and generates trace data. Complexity: LOW.

**V2 (Real Orchestrator):** Once the protocol is validated and we have eval data showing where role-switching causes quality issues, build the real orchestrator with separate API calls per agent. Complexity: HIGH, but now justified by evidence.

**Practical implication:** Phase 2 in the plan should be split:
- **Phase 2A**: Simulated MOE (Lead Editor role-switches, single session) — build first
- **Phase 2B**: Real orchestrator with separate API calls — build when Phase 2A evals show cross-agent pollution

This follows our own "start cheap, upgrade on evidence" principle.

---

### 4. Branching/Undo Strategy — AGREE, SHOULD HAVE CAUGHT THIS

**The reviewer caught a real gap.** The plan has cascade *warnings* for upstream revisions but no mechanism to actually undo. If you realize Act 2 was wrong after writing 5 chapters of it, you need to roll back to a known good state — and with append-only relationships.yaml + scattered canon files, manual undo is painful.

**What I'd change:**

**Mandatory git commit at every step completion:**

```python
# In Phase 4: Commit
def commit_step(step_name, artifact_path):
    # 1. Write artifact
    write_canonical_artifact(artifact_path)
    
    # 2. Update relationships.yaml
    update_relationships(changes)
    
    # 3. Git commit with structured message
    git_commit(
        message=f"pipeline: {step_name} complete",
        tag=f"step/{step_name}"  # e.g., step/act2-outline
    )
    
    # 4. Record commit hash in decision log
    append_decision_log(step_name, commit_hash=get_head())
```

**Undo = git checkout:**

```bash
# "Undo Act 2 outline and everything after it"
git log --oneline --grep="pipeline:"
# Shows: step/act2-ch3-scene1, step/act2-ch2, step/act2-ch1, 
#        step/act2-outline, step/act1-complete

git checkout step/act1-complete -- canon/ .pipeline-state.yaml
# Reverts canon/ and pipeline state to exactly where Act 1 ended
```

The decision log + git tags give you **named restore points** aligned to every step in the pipeline. This is lightweight (git is already in the workflow) and handles the novel-scale undo problem cleanly.

---

### 5. Evaluation Fatigue — STRONGLY AGREE, BEST INSIGHT IN THE REVIEW

**This is the finding I should have anticipated.** Writers want to write, not fill in evaluation forms. Asking them to score 5 dimensions per agent comment after every mob session will be abandoned within a week.

**What I'd change:**

**Implicit scoring as the default:**

| Human Action | Implicit Score | Rationale |
|-------------|----------------|-----------|
| Accepts comment without edit | quality=5, relevance=5 | They agreed completely |
| Accepts with minor edits | quality=4, relevance=4 | Good direction, needed refinement |
| Engages in back-and-forth then accepts | quality=3, relevance=4 | Needed discussion but was relevant |
| Rejects comment | quality=1, relevance=2 | Not useful |
| Ignores comment (skips without responding) | quality=2, relevance=1 | Not worth engaging with |

The orchestrator **automatically captures these signals** from the conversation flow. No forms, no annotation, no extra work.

**Explicit annotation becomes optional and rare:**

The `<!-- HUMAN-EVAL: ... -->` templates still exist in trace files, but they're for when the human WANTS to leave specific feedback — like "this comment was technically correct but missed the tone I'm going for" or "upgrade this agent's model." This happens maybe 1 in 10 times, not every time.

**Model adequacy signal changes too:**

Instead of `model-adequate=yes/no`, derive it from patterns:
- If an agent's comments are consistently rejected (>60% over 5 traces) → likely model-inadequate
- If an agent's comments trigger multi-turn discussion that usually ends in acceptance → model is working, maybe prompt needs tuning
- If an agent's comments are consistently accepted immediately → model is fine, possibly underutilized

This preserves the eval-driven upgrade loop without burdening the writer.
