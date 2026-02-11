---
name: Story Arc Builder
description: Convert a story concept into a full arc architecture with act progression, character trajectories, subplot map, and thematic pressure points. Produces canon/story-arc.md.
---

# Story Arc Builder Skill

Convert a Level 1 story concept into a complete arc architecture at Level 2. Establishes the structural skeleton that all act outlines and downstream work depend on.

## Usage
```
/project:skills:story-arc-builder {concept_file}
```

## Process

### Inputs
- **Required**: `concept_file` (path to `canon/story-concept.md`)
- **Optional**: `target_scope` (default: "full_story"), `act_count` (default: 4), `character_files` (paths to character profiles)

### Context Files
Load (required):
- `canon/story-concept.md` — the L1 concept artifact (FAIL if missing)

Load if present:
- `canon/relationships.yaml` — entity roster and aliases
- `canon/characters/*.md` — character profiles
- `canon/preferences.md` — user style/content preferences
- `templates/story-arc.template.md` — output structure

### Steps
1. Verify `canon/story-concept.md` exists. If missing, halt and inform the user that L1 must be completed first.
2. Load `templates/story-arc.template.md` as the output structure.
3. Load the story concept and extract: premise, genre, controlling idea, central dramatic question, stakes, story promise, setting.
4. Load character profiles and relationships if available.
5. Generate the arc by working through each template section:
   - **Arc Overview**: One-paragraph summary of the full story arc.
   - **Act Progression**: Break the story into acts (default 4-part: Act 1, Act 2A, Act 2B, Act 3). For each act, define the key beats, dramatic function, and how it advances the central dramatic question.
   - **Character Trajectories**: For each major character, define their state at the start and end of each act. Show how each character changes across the arc.
   - **Subplot Map**: Identify subplot threads and their touchpoints per act.
   - **Thematic Pressure Points**: Identify where the controlling idea is tested, challenged, or reinforced in each act.
   - **Open Questions**: Surface unresolved design decisions for act outlines to address.
   - **Sources**: List all canon files consulted.
6. Write the completed artifact to `canon/story-arc.md`.
7. For each new relationship implied by the arc, output ready-to-run commands:
   ```
   python scripts/relationship_query.py add --file canon/relationships.yaml \
     --from [entity] --to [entity] --rel [rel_type] \
     --context "[context]" --established L2/arc \
     --source "canon/story-arc.md"
   ```

### State Update
After successful completion, update `.pipeline-state.yaml`:
- `position.level`: `L2` → `L3`
- `position.act`: remains `null` (user chooses which act to outline first)

## Output Format
The output must conform to `templates/story-arc.template.md` with all `##` sections populated. No placeholder comments (`<!-- -->`) should remain in the final output.

## Quality Checks
- Every `##` section from the template is present and populated.
- Arc explicitly references constraints from `canon/story-concept.md` (controlling idea, CDQ, stakes).
- Character trajectories show meaningful change across acts (not static).
- Each act has a distinct dramatic function (not just "stuff happens").
- Subplot map connects to the main arc (no orphan subplots).
- Thematic pressure points escalate through the arc.
- Open questions are specific and actionable (not vague).
- No forbidden vocabulary (delve, multifaceted, etc.).
