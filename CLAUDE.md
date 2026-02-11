# Fiction Writing Skills System - Project Guide

## Repository Overview
This repository contains the Fiction Writing Skills System, a Claude Code skill set for producing research-informed, high-quality fiction.

## Core Principles
1. **Story Grid Alignment**: Every scene must follow the Five Commandments and have a clear value shift.
2. **Character Voice**: All prose is filtered through a character-specific Voice Profile.
3. **Anti-AI Prose**: Strict enforcement of forbidden vocabulary and human-like sentence variation.
4. **World Consistency**: Hard constraints and scene tracking prevent continuity errors.

## Key Directories
- `templates/`: Foundational templates for Bible, Characters, World, and Tracking.
- `canon/`: Active story reference documents (Story Bible, World Rules, Timeline).
- `characters/`: Detailed character profiles with Voice Profiles.
- `.claude/commands/skills/`: Individual skill definitions.

## Primary Commands
- `/project:pipeline-run {scene_path}`: Orchestrate the full 3-stage pipeline.
- `/project:skills:voice-anchor`: Set or verify the narrative voice.
- `/project:skills:scene-architect`: Plan scenes with Story Grid structure.
- `/project:skills:scene-draft`: Generate prose with voice/rule enforcement.

## Foundation Setup
Before drafting, ensure these are populated:
1. `canon/world/story-bible.md` (from `templates/story-bible.template.md`)
2. `canon/world/world-rules.md` (from `templates/world-rules.template.md`)
3. `canon/timeline.md` (from `templates/scene-tracker.template.md`)
4. `characters/{name}.md` (from `templates/character-profile.template.md`)

## Writing Checklist
- [ ] POV character's internal voice matches their profile
- [ ] No forbidden vocabulary (delve, multifaceted, etc.)
- [ ] At least 2 non-visual sensory details per scene
- [ ] Scene has a Crisis (Best Bad Choice or Irreconcilable Goods)
- [ ] Value shift is achieved and logical
