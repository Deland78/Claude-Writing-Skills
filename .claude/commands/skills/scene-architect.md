# Scene Architect Skill

Convert chapter promise + tension map into structured scene cards with goal, obstacle, turn, cost, and exit hook.

## Usage
```
/project:skills:scene-architect {chapter_promise_output} {tension_map_output}
```

## Process

### Inputs
- **Required**: `chapter_promise_output`, `tension_map_output`
- **Optional**: `character_bible`, `setting_notes`

### Steps
1. Generate 3-7 scene cards.
2. Each card includes: POV, location, time, goal, obstacle, tactic, turn, cost, exit emotion, next hook.
3. Ensure each scene has a TURN that changes the situation.
4. Ensure each scene ends with propulsion (not closure).

## Output Format
- scenes:
  - id:
    pov:
    location:
    time:
    goal:
    obstacle:
    tactic:
    # Five Commandments
    inciting_incident:
    progressive_complication:
    crisis_type: best_bad_choice | irreconcilable_goods
    crisis_question:
    climax_action:
    resolution:
    value_shift: [from] -> [to]
    # Original progression
    turn:
    cost:
    exit_emotion:
    next_hook:

## Quality Checks
- Every scene has a goal and an obstacle.
- Every scene has a turn and a cost.
- No scene exists only to deliver exposition.
