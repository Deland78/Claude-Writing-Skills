# AI Co-Author System Plan (SF-Thriller + SF-Philosophical)

## Purpose
Design a flexible, opinionated AI co-author system that assists (not teaches) a fiction writer in generating ideas, drafting scenes, diagnosing issues, and proposing high-quality alternatives. The system is optimized for SF-Thriller + SF-Philosophical fiction and is built for human-in-the-loop collaboration with explicit review checkpoints.

## Guiding Principles
1. **Co-author, not tutor**: Provide options, critiques, and solutions without lecturing.
2. **Opinionated + proactive**: Detect issues (continuity, tropes, generic dialogue) and recommend upgrades.
3. **Human-in-the-loop by default**: Pause for review after each major stage.
4. **Long-term learning**: Ask to confirm preference updates; improve skills/tools over time.
5. **What-if by request**: Branching variants only when explicitly asked.
6. **Single canonical source of truth**: Maintain a unified, authoritative canon.
7. **Write in the user’s style by default**: Drafts emulate the writer’s voice unless they request a different profile.

## System Outcomes
- High-quality plot and character ideation with rapid iteration.
- Scene drafts that respect canon, continuity, and world rules.
- Automated detection of tropey or generic material with fresher alternatives.
- Explicit feedback loops so the system evolves with the writer’s tastes.

---

## Architecture Overview

### Core Roles (Multi-Agent, Opinionated)
1. **Lead Story Editor (Orchestrator)**
   - Owns workflow routing, progress summaries, and decision points.
   - Requests approvals at stage boundaries.

2. **Plot & Structure Analyst**
   - High-level plot options, tension curves, reversals, causality checks.
   - Detects stalls or flat momentum and proposes fixes.

3. **Character & Voice Specialist**
   - Character psychology, voice fidelity, and uniqueness checks.
   - Flags stereotypes and generic dialogue, proposes rewrites.

4. **Continuity & Canon Keeper**
   - Automatic continuity checks (timeline, knowledge, objects, rules).
   - Enforces single-canon updates and flags contradictions.

5. **Conceptual Depth Partner**
   - Guards philosophical depth: ethical dilemmas, intellectual tension.
   - Ensures concept meaningfully pressures plot and character choices.

6. **Prose & Rhythm Crafter**
   - Optional line-level refinement when requested.

### Memory & Context Strategy (Design Decision)
**Recommended: Modular knowledge base with selective retrieval + canonical registry.**

**Why**:
- **Scale & accuracy**: Modular docs (character, tech, location) allow targeted retrieval.
- **Performance**: Smaller context windows improve relevance and reduce drift.
- **Governance**: A canonical registry file maps each module and acts as the single source of truth.

**Implementation Pattern**:
- `canon/index.md` (single canonical index + change log)
- `canon/characters/{name}.md`
- `canon/world/{location}.md`
- `canon/tech/{system}.md`
- `canon/themes/{theme}.md`
- `canon/timeline.md`

The system always reads the index + only the relevant modules for the task.

---

## Workflow Stages (Human-in-the-Loop)

### Stage 0: Seed + Intent
**Input**: Concept, vibe, constraints, tone.
**Output**: 2–3 optional story trajectories + key differentiators.
**Pause for approval**: Choose preferred trajectory.

### Stage 1: Canon Setup (Single Source of Truth)
**Input**: Approved trajectory.
**Output**: Canon registry + initial modules (world, theme, characters).
**Pause for approval**: Confirm canon baseline.

### Stage 2: Plot & Philosophy Architecture
**Output**:
- Plot spine with act-level beats.
- Philosophical pressure points (dilemmas that force action).
- Tension curve checkpoints.
**Pause for approval**: Lock the structural plan.

### Stage 3: Scene Blueprinting
**Output**: Scene blueprints with value shifts, stakes, and reversals.
**Automatic checks**: Causality, escalation, POV fit.
**Pause for approval**.

### Stage 4: Drafting (Full Scene Drafts)
**Output**: Drafted scenes in the user’s style and voice alignment.
**Automatic checks**:
- Continuity compliance
- Trope/generic dialogue detection
- Philosophical depth alignment
**Pause for approval**.

### Stage 5: Diagnostics + Alternatives
**Output**:
- Issue list: trope flags, flat sections, missed opportunities.
- 2–3 alternative fixes per issue.
**Pause for approval**.

---

## Proactive Quality Diagnostics (Auto-Run)
- **Continuity**: timeline, objects, knowledge state, location constraints.
- **Trope/Garbage Detector**: cliché patterns, stereotyped dialogue, generic beats.
- **Conceptual Alignment**: philosophical dilemma must influence plot choices.
- **Scene Vitality**: value shift, stakes pressure, decision force.
- **Voice Distinctness**: ensure character speech is differentiated.

Each issue includes: context, why it’s weak, and multiple alternatives.

---


## Style Modeling Protocol
- User supplies voice/style samples as the primary style source (minimum 3 passages).
- The system builds an explicit style profile from those samples before first drafting.
- The profile is refined over time using approved edits, with confirmation prompts before major updates.

---

## Preference Learning Loop
After major milestones, the system asks to update preferences:
- “Do you prefer tighter pacing or deeper introspection here?”
- “Are these kinds of twists working for you?”

Updates are written to a `preferences.md` canon module.

---

## “What If” Exploration (On Demand)
- Triggered only by explicit request.
- Generates 2–3 alternative branches, each with:
  - New causal chain
  - Impact on character arc
  - Continuity implications
  - Pros/cons

---

## Interfaces / Implementation Paths (Beyond Claude Code)
1. **Agent-Orchestrated CLI** (Codex/Claude Code style)
2. **Story Graph UI** (visual branching + canon locking)
3. **Notebook Workflow** (prompt blocks + deterministic outputs)
4. **IDE Plugin** (sidecar panel for diagnostics + variants)

---

## Next Steps (If Approved)
1. Define canonical file structure + templates.
2. Draft skill specs for each agent role.
3. Build prototype pipeline with 2–3 stages (Seed → Canon → Plot).
4. Conduct a pilot run on a single SF-Thriller/Philosophical concept.

---

## Open Questions (Single-Question Flow)
Continue interview one question at a time.
