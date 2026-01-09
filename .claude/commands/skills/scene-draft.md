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
1. BEFORE DRAFTING: Load and verify against World Rules hard constraints.
2. Start with sensory grounding + immediate stakes.
3. Establish POV desire in the first 10% of scene.
4. Escalate through proximity, power, or urgency.
5. DURING DRAFTING: Enforce POV character's voice profile (sentence rhythm, vocabulary, what they notice).
6. Insert micro-exposition only when triggered by action/object/memory.
7. Execute the turn: reversal, discovery, decision, or interruption.
8. End on propulsion: a threat, question, consequence, or uneasy relief.
9. AFTER DRAFTING: Verify against anti-AI checklist.

## Output Format
- Drafted scene
- Beat list (1 line each): entry / escalation / turn / exit

## Quality Checks
- [ ] No words from forbidden vocabulary list.
- [ ] Sentence lengths vary (5-25 words, no patterns).
- [ ] At least 2 non-visual sensory details present (sound, texture, light, temperature, smell).
- [ ] No three consecutive sentences with same structure.
- [ ] Specific details, not generic descriptors.
- [ ] Turn changes the state of the story.
- [ ] Exit hook forces movement to next scene.
