# Scene Draft Skill

Draft a single scene in Watcher voice with clear beats, sensory grounding, conflict, turn, and a strong exit hook.

## Usage
```
/project:skills:scene-draft {scene_card}
```

## Process

### Inputs
- **Required**: `scene_card`
- **Optional**: `voice_anchor` (default: "watcher_voice_anchor"), `target_word_count`

### Steps
1. Start with sensory grounding + immediate stakes.
2. Establish POV desire in the first 10% of scene.
3. Escalate through proximity, power, or urgency.
4. Insert micro-exposition only when triggered by action/object/memory.
5. Execute the turn: reversal, discovery, decision, or interruption.
6. End on propulsion: a threat, question, consequence, or uneasy relief.

## Output Format
- Drafted scene
- Beat list (1 line each): entry / escalation / turn / exit

## Quality Checks
- At least 2 sensory details present (sound, texture, light, temperature, smell).
- Turn changes the state of the story.
- Exit hook forces movement to next scene.
