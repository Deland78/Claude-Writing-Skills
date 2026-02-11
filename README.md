# Fiction Writing Skills System - Product Documentation

## Document Index

| Document | Description | Status |
|----------|-------------|--------|
| [01_PRODUCT_ROADMAP.md](01_PRODUCT_ROADMAP.md) | Three-phase roadmap with research foundation, features, success criteria, and feedback touchpoints | Complete |
| [02_PHASE1_PRDs.md](02_PHASE1_PRDs.md) | Detailed Product Requirements Documents for all Phase 1 MVP features | Complete |
| [03_IMPLEMENTATION_GUIDE.md](03_IMPLEMENTATION_GUIDE.md) | Technical implementation guide for Claude Code, including file structures, command definitions, and templates | Complete |
| [05_AI_COAUTHOR_PLAN.md](05_AI_COAUTHOR_PLAN.md) | Opinionated AI co-author architecture for SF-thriller / SF-philosophical writing with style modeling and diagnostics | Complete |
| [06_COAUTHOR_EXECUTION_RUNBOOK.md](06_COAUTHOR_EXECUTION_RUNBOOK.md) | Operational runbook for canon setup and deterministic validation | Complete |
| [07_COAUTHOR_SYSTEM_DESIGN.md](07_COAUTHOR_SYSTEM_DESIGN.md) | Detailed system design with architecture and end-to-end flow diagram | Complete |

---

## Executive Summary

This product creates a **hybrid skill/agent system for Claude Code** that helps fiction writers produce consistent, craft-informed scenes while maintaining creative control.

### Core Problem Solved
AI-assisted scene drafting frequently loses:
- Character voice consistency
- Continuity details (knowledge, objects, timeline)
- World rule compliance (magic systems, geography)
- Authentic prose quality (avoids AI "tells")

### Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Story Bible (Foundation)                  │
│  story-bible.md | world-rules.md | scene-tracker.md         │
│  characters/*.md                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Phase 1: MVP Pipeline                     │
│                                                              │
│  outline.md → [Scene Architect] → blueprint.md               │
│                      ↓ pause for review                      │
│  blueprint.md → [Scene Draft] → draft.md                     │
│                      ↓ pause for review                      │
│  draft.md → [Character Truth] → audit.md                     │
│                      ↓                                       │
│                 [Human Polish]                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Phase 2: Agents (Future)                  │
│                                                              │
│  Scene Director (diagnoses, orchestrates)                    │
│       ├── Prose Surgeon (line-level craft)                   │
│       └── Continuity Keeper (cross-references)               │
│                                                              │
│  Additional Skills:                                          │
│  - Dialogue Subtext Pass                                     │
│  - Tension Curve Analysis                                    │
│  - AI Humanization Pass                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Phase 3: Scale (Future)                   │
│                                                              │
│  - Multi-scene arc tracking                                  │
│  - Voice fingerprinting                                      │
│  - Genre-specific modules                                    │
│  - Collaboration features                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Research Foundation

The system is grounded in proven craft methodologies:

### Story Grid (Shawn Coyne)
- **Five Commandments**: Every scene has Inciting Incident, Progressive Complication, Crisis, Climax, Resolution
- **Value Shift**: Every scene must change something
- **Scene Purpose**: Reveal character, setting, context, or advance plot

### Stephen King's "On Writing"
- Write first draft fast, revise ruthlessly
- Show don't tell (avoid adverbs, use active voice)
- Natural dialogue (your vocabulary, not thesaurus words)
- Kill your darlings (cut 10%+)

### Character Voice Craft
- Voice = how character interprets the world (worldview filter)
- Consistency builds trust
- Subtext matters (what's NOT said)
- Differentiation: syntax, rhythm, vocabulary, tics

### Anti-AI Prose Patterns
System actively counters:
- Over-consistency (uniform sentences)
- Regression to mean (generic descriptions)
- Overused vocabulary ("delve," "multifaceted," etc.)
- Lack of sensory variety
- Missing concrete details

---

## Phase 1 MVP Features

### 1.1 Story Bible Schema
Structured templates for tracking story facts:
- `story-bible.md` - premise, theme, structure
- `characters/*.md` - profiles with voice guides
- `world-rules.md` - constraints and hard limits
- `scene-tracker.md` - continuity tracking

### 1.2 Scene Architect Skill
Transform rough idea → structured blueprint following Five Commandments

### 1.3 Scene Draft Skill
Transform blueprint → full prose with voice enforcement and world rule checking

### 1.4 Character Truth Pass
Audit draft for character consistency (voice, knowledge, behavior)

### 1.5 Pipeline Runner
Orchestrate skills with pause-for-review between stages

---

## Success Criteria (MVP)

1. Writer produces complete scene from outline in under 2 hours
2. Character voice remains consistent across scenes
3. No world rule violations in generated content
4. Prose passes "gut check" for human quality
5. Writer maintains creative control at each stage

---

## Customer Feedback Integration

### Post-Phase 1 Interview (After MVP)
- What's working/not working?
- Are templates capturing what you need?
- Voice preservation accuracy?
- What's missing?

### Post-Phase 2 Interview (After Agents)
- Scene Director diagnosis accuracy?
- Prose Surgeon helpfulness?
- Continuity error catch rate?
- What's the new bottleneck?

---

## Getting Started

### Quick Start: Stage 0 (Story Development)
1. Validate setup: `python scripts/validate_coauthor_setup.py --root .`
2. Run `/project:skills:story-concept` → produces `canon/story-concept.md` (L1)
3. Run `/project:skills:story-arc-builder` → produces `canon/story-arc.md` (L2)
4. Run `/project:skills:act-outline` (per act) → produces `canon/acts/act-{N}-outline.md` (L3)
5. Pipeline state advances automatically through L1→L2→L3 in `.pipeline-state.yaml`
6. Continue to Stage 1 (chapter planning) with `/project:pipeline-run`

### Mob Review (Mode C)

At any pipeline step, run a mob review where specialist agents critique the current artifact:

```
/project:skills:mob-session
```

The Lead Editor orchestrates specialist agents (Plot Analyst, Character Specialist, Depth Partner, Continuity Agent, Prose Crafter) in a structured 4-phase protocol:
1. **Structure Offer** — organizes your input
2. **Comment Queue** — each agent gives one focused comment with canon citations
3. **Resolution Check** — summarizes accepted changes, checks governance rules
4. **Commit** — writes approved changes to canon files

You maintain full control: accept, reject, revise, or park each suggestion. See `docs/mob_protocol.md` for details.

### Background Reading
1. Read [01_PRODUCT_ROADMAP.md](01_PRODUCT_ROADMAP.md) for full context
2. Review [02_PHASE1_PRDs.md](02_PHASE1_PRDs.md) for detailed requirements
3. Use [03_IMPLEMENTATION_GUIDE.md](03_IMPLEMENTATION_GUIDE.md) to build the system
4. Review [05_AI_COAUTHOR_PLAN.md](05_AI_COAUTHOR_PLAN.md) for the opinionated co-author architecture
5. Run [06_COAUTHOR_EXECUTION_RUNBOOK.md](06_COAUTHOR_EXECUTION_RUNBOOK.md) and validate setup with `python scripts/validate_coauthor_setup.py --root .`

---

## Version

- **Version**: 0.1.0
- **Date**: January 8, 2026
- **Status**: Phase 1 documented, ready for implementation
