# Pipeline Run

Orchestrate the full fiction writing pipeline with state management and review pauses.

## Usage
```
/project:pipeline-run {scene-directory}
```

## Process

### Stage 0: Story Development
1. Load skill: `.claude/skills/story-concept/SKILL.md`
   - Output: `canon/story-concept.md`
   - State: L1 → L2
2. **PAUSE**: Human review of story concept.
3. Load skill: `.claude/skills/story-arc-builder/SKILL.md`
   - Output: `canon/story-arc.md`
   - State: L2 → L3
4. **PAUSE**: Human review of story arc.
5. Load skill: `.claude/skills/act-outline/SKILL.md` (per act)
   - Output: `canon/acts/act-{N}-outline.md`
   - State: L3 (advance act pointer)
6. **PAUSE**: Human review of all act outlines before Stage 1.

### Stage 1: Chapter Planning
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
The pipeline tracks progress in `.pipeline-state.yaml` at the project root.
If interrupted, rerunning the command will resume from the last incomplete stage.

### State Transitions
| After Step | Position | Ready For |
|------------|----------|-----------|
| story-concept | L2 | Arc building |
| story-arc-builder | L3, act: null | Act outlining |
| act-outline(N) | L3, act: N | Next act or L4 |
| All acts outlined | L4, act: 1 | Chapter planning |
