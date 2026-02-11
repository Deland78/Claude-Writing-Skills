# Fiction Writing Skills System - Project Guide

## Repository Overview
This repository contains the Fiction Writing Skills System, a Claude Code skill set for producing research-informed, high-quality fiction.

## Core Principles
1. **Story Grid Alignment**: Every scene must follow the Five Commandments and have a clear value shift.
2. **Character Voice**: All prose is filtered through a character-specific Voice Profile.
3. **Anti-AI Prose**: Strict enforcement of forbidden vocabulary and human-like sentence variation.
4. **World Consistency**: Hard constraints and scene tracking prevent continuity errors.

## Key Directories
- `templates/`: Foundational templates for Story Concept, Arc, Act Outline, Characters, World, and Tracking.
- `canon/`: Active story reference documents and hierarchical story structure.
  - `canon/story-concept.md`: L1 story concept output.
  - `canon/story-arc.md`: L2 arc architecture output.
  - `canon/acts/`: L3 act outlines (`act-{N}-outline.md`).
  - `canon/world/`: Story Bible and World Rules.
  - `canon/characters/`: Character profiles.
  - `canon/relationships.yaml`: Entity-relationship tracking.
- `schemas/`: JSON Schema definitions for pipeline contracts.
- `scripts/`: Pipeline support tools (context loader, validators, relationship query).
- `.claude/skills/`: Individual skill definitions.

## Primary Commands
- `/project:pipeline-run {scene_path}`: Orchestrate the full 4-stage pipeline (Stage 0–3).
- `/project:skills:story-concept`: Generate L1 story concept → `canon/story-concept.md`.
- `/project:skills:story-arc-builder`: Generate L2 arc → `canon/story-arc.md`.
- `/project:skills:act-outline`: Generate L3 act outline → `canon/acts/act-{N}-outline.md`.
- `/project:skills:voice-anchor`: Set or verify the narrative voice.
- `/project:skills:scene-architect`: Plan scenes with Story Grid structure.
- `/project:skills:scene-draft`: Generate prose with voice/rule enforcement.

## Foundation Setup
Before drafting, ensure these are populated:

### Stage 0: Story Development (L1–L3)
1. Run `/project:skills:story-concept` → `canon/story-concept.md`
2. Run `/project:skills:story-arc-builder` → `canon/story-arc.md`
3. Run `/project:skills:act-outline` (per act) → `canon/acts/act-{N}-outline.md`

### Supporting Files
- `canon/world/story-bible.md` (from `templates/story-bible.template.md`)
- `canon/world/world-rules.md` (from `templates/world-rules.template.md`)
- `canon/timeline.md` (from `templates/scene-tracker.template.md`)
- `canon/characters/{name}.md` (from `templates/character-profile.template.md`)
- `.pipeline-state.yaml` — pipeline position and agent configuration

## Writing Checklist
- [ ] POV character's internal voice matches their profile
- [ ] No forbidden vocabulary (delve, multifaceted, etc.)
- [ ] At least 2 non-visual sensory details per scene
- [ ] Scene has a Crisis (Best Bad Choice or Irreconcilable Goods)
- [ ] Value shift is achieved and logical
