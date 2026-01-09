# Pipeline Run

Orchestrate the full fiction writing pipeline with state management and review pauses.

## Usage
```
/project:pipeline-run {scene-directory}
```

## Process

### Stage 1: Planning
1. Run `/project:skills:chapter-promise`
2. Run `/project:skills:tension-curve`
3. Run `/project:skills:scene-architect`
4. **PAUSE**: Human review of scene cards.

### Stage 2: Drafting
1. Run `/project:skills:voice-anchor` (if needed)
2. Run `/project:skills:scene-draft`
3. **PAUSE**: Human review of draft prose.

### Stage 3: Revision
1. Run `/project:skills:character-truth`
2. Run `/project:skills:dialogue-subtext`
3. Run `/project:skills:line-tightening`
4. Run `/project:skills:ai-filter-humanize`
5. Run `/project:skills:continuity-callback`
6. Run `/project:skills:final-polish`
7. **PAUSE**: Final editorial review and git commit.

## State Management
The pipeline tracks progress in `{scene-directory}/.pipeline-state`. 
If interrupted, rerunning the command will resume from the last incomplete stage.
