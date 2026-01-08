# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **product documentation repository** for the Fiction Writing Skills System - a Claude Code skill/agent system that helps fiction writers produce consistent, craft-informed scenes. The repository contains planning documents, PRDs, and implementation specifications - **not code**.

## Document Structure

| Document | Purpose |
|----------|---------|
| `01_PRODUCT_ROADMAP.md` | Three-phase roadmap: research foundation, features by phase, success criteria |
| `02_PHASE1_PRDs.md` | Detailed requirements for Phase 1 MVP (Story Bible Schema, Scene Architect, Scene Draft, Character Truth, Pipeline Runner) |
| `03_IMPLEMENTATION_GUIDE.md` | Technical specs including file structures, command definitions, YAML skill definitions, and templates |

## Core Concepts

### Story Grid Five Commandments
Every scene blueprint must contain:
1. **Inciting Incident** (causal or coincidental)
2. **Progressive Complications** with a turning point
3. **Crisis** (Best Bad Choice or Irreconcilable Goods)
4. **Climax** (choice + action)
5. **Resolution** with value shift

### Anti-AI Prose Requirements
Drafts must avoid: delve, multifaceted, navigate, foster, embark, journey, landscape, testament, unwavering, intricate, beacon, realm, pivotal, nuance, crucial, indispensable, comprehensive, furthermore, consequently, hence, vital

Drafts must include: varied sentence lengths, 2+ non-visual sensory details, specific concrete details

## Phase 1 Skills (Specified)

- **Scene Architect**: `outline.md` → `blueprint.md` (Story Grid structure)
- **Scene Draft**: `blueprint.md` → `draft.md` (prose with voice/world enforcement)
- **Character Truth**: `draft.md` → `audit.md` (consistency checks)
- **Pipeline Runner**: Orchestrates all three with review pauses

## Target Directory Structure (for implementation)

```
{project}/
├── .claude/commands/skills/     # Skill command definitions
├── bible/                       # story-bible.md, world-rules.md, scene-tracker.md
├── characters/                  # {name}.md profiles
├── chapters/ch{XX}/scene-{XX}/  # outline.md, blueprint.md, draft.md, audit.md
└── templates/                   # Template files for bible/characters
```

## When Working With These Documents

- Phase 1 is fully specified and ready for implementation
- Phases 2-3 are placeholders awaiting Phase 1 feedback
- The `03_IMPLEMENTATION_GUIDE.md` contains copy-pasteable file contents for building the actual system
- YAML skill definitions in the implementation guide define inputs, context loading, validation rules, and anti-AI patterns
