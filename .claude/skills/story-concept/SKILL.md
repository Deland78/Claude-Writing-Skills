---
name: Story Concept
description: Generate a structured story concept artifact at L1, incorporating the story-promise framework. Produces canon/story-concept.md.
---

# Story Concept Skill

Generate a structured story concept artifact at Level 1. This is the foundational document from which all downstream arc, act, and chapter work derives.

## Usage
```
/project:skills:story-concept {genre} {protagonist} {inciting_situation}
```

## Process

### Inputs
- **Required**: `genre`, `protagonist`, `inciting_situation`
- **Optional**: `comparable_titles`, `world_premise`, `target_length`

### Context Files
Load if present:
- `canon/world/story-bible.md` — existing world context
- `canon/preferences.md` — user style/content preferences
- `templates/story-concept.template.md` — output structure

### Steps
1. Validate that all required inputs are provided. If any are missing, prompt for completion rather than producing partial output.
2. Load `templates/story-concept.template.md` as the output structure.
3. Load available canon context files.
4. Generate the story concept by working through each template section:
   - **Premise**: Synthesize genre + protagonist + inciting situation into a 1-2 paragraph concept.
   - **Genre**: Identify primary and secondary genres.
   - **Controlling Idea**: Derive the thematic statement in "Value is achieved/lost when condition" format.
   - **Central Dramatic Question**: Identify the single question driving the narrative.
   - **Stakes**: Define what is at risk, for whom, and why it matters.
   - **Story Promise**: Apply the story-promise framework — what kind of story is this? What central question drives it? What stakes will be resolved? Write a promise statement (1 paragraph).
   - **Point of View**: Determine POV type and protagonist details.
   - **Setting**: Establish time, place, and technology level.
   - **Target Scope**: Set word count, chapter count, and act structure targets.
   - **Sources**: List all canon files consulted.
5. Write the completed artifact to `canon/story-concept.md`.
6. If a protagonist entity does not yet exist in `canon/relationships.yaml`, output a ready-to-run command to add it:
   ```
   python scripts/relationship_query.py add --file canon/relationships.yaml ...
   ```

### State Update
After successful completion, update `.pipeline-state.yaml`:
- `position.level`: `L1` → `L2`
- `position.act`: remains `null`

## Output Format
The output must conform to `templates/story-concept.template.md` with all `##` sections populated. No placeholder comments (`<!-- -->`) should remain in the final output.

## Quality Checks
- Every `##` section from the template is present and populated.
- Controlling idea follows "Value is achieved/lost when condition" format.
- Central dramatic question is specific and answerable (not generic).
- Stakes are concrete and personal (not abstract).
- Story promise is honest — it matches what the concept actually delivers.
- No forbidden vocabulary (delve, multifaceted, etc.).
- Sources section lists actual files consulted.
