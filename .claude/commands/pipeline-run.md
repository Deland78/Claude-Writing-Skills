# Pipeline Run

Orchestrate the full fiction writing pipeline with state management and review pauses.

## Usage
```
/project:pipeline-run {scene-directory}
```

## Process

### Stage 1: Planning
1. Load skill: `.claude/skills/chapter-promise/SKILL.md`
2. Load skill: `.claude/skills/tension-curve/SKILL.md`
3. Load skill: `.claude/skills/scene-architect/SKILL.md`
4. **PAUSE**: Human review of scene cards.

### Stage 2: Drafting
1. Load skill: `.claude/skills/voice-anchor/SKILL.md` (if needed)
2. Load skill: `.claude/skills/scene-draft/SKILL.md`
3. **PAUSE**: Human review of draft prose.

### Stage 3: Revision
1. Load skill: `.claude/skills/character-truth/SKILL.md`
2. Load skill: `.claude/skills/dialogue-subtext/SKILL.md`
3. Load skill: `.claude/skills/line-tightening/SKILL.md`
4. Load skill: `.claude/skills/ai-filter-humanize/SKILL.md`
5. Load skill: `.claude/skills/continuity-callback/SKILL.md`
6. Load skill: `.claude/skills/final-polish/SKILL.md`
7. **PAUSE**: Final editorial review and git commit.

## State Management
The pipeline tracks progress in `{scene-directory}/.pipeline-state`. 
If interrupted, rerunning the command will resume from the last incomplete stage.
