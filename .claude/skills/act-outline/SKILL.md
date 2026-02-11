---
name: Act Outline
description: Produce a per-act chapter-level outline with beat intent, value shifts, causal dependencies, and continuity touchpoints. Produces canon/acts/act-{N}-outline.md.
---

# Act Outline Skill

Expand a single act from the story arc into a chapter-level outline at Level 3. Each chapter gets beat intent, value shift, causal dependency, and key characters.

## Usage
```
/project:skills:act-outline {arc_file} {act_number}
```

## Process

### Inputs
- **Required**: `arc_file` (path to `canon/story-arc.md`), `act_number` (integer, >= 1)
- **Optional**: `chapter_count_hint` (suggested chapter count for this act)

### Context Files
Load (required):
- `canon/story-arc.md` — the L2 arc artifact (FAIL if missing)

Load if present:
- `canon/story-concept.md` — for controlling idea and CDQ reference
- `canon/acts/act-*-outline.md` — sibling act outlines for cross-act awareness
- `canon/characters/*.md` — character profiles
- `canon/relationships.yaml` — entity roster and relationships
- `templates/act-outline.template.md` — output structure

### Steps
1. Validate `act_number` (must be >= 1). Verify `canon/story-arc.md` exists. If missing, halt and inform the user that L2 must be completed first.
2. Load `templates/act-outline.template.md` as the output structure.
3. Load the story arc and extract the relevant act's progression, character trajectories, subplot touchpoints, and thematic pressure for this act.
4. Load sibling act outlines if they exist (for continuity and cross-act awareness).
5. Generate the act outline by working through each template section:
   - **Act Overview**: Summarize the act's dramatic function and where it sits in the arc.
   - **Chapter List**: For each chapter in this act, define:
     - Chapter title/number
     - Beat intent (what must happen)
     - Value shift (polarity change, e.g., safety → danger)
     - Causal dependency (what prior event enables this chapter)
     - Key characters present
     - Brief summary (2-3 sentences)
   - **Continuity Touchpoints**: List entities, facts, and timeline constraints that downstream chapters must respect. This is a structured output section — the continuity agent sidecar (Phase 3) will consume it later.
   - **Open Questions**: Surface items needing resolution before chapter-level work.
   - **Sources**: List all canon files consulted.
6. Write the completed artifact to `canon/acts/act-{N}-outline.md`.

### State Update
After successful completion, update `.pipeline-state.yaml`:
- `position.level`: remains `L3`
- `position.act`: set to `{N}` (the act just outlined)
- When all acts are outlined and the user is ready to proceed: advance to `level: L4, act: 1, chapter: null`

## Output Format
The output must conform to `templates/act-outline.template.md` with all `##` sections populated. No placeholder comments (`<!-- -->`) should remain in the final output.

## Quality Checks
- Every `##` section from the template is present and populated.
- Chapters are ordered with sequential numbering.
- Every chapter has a beat intent and a value shift.
- At least one causal dependency per chapter (except the first chapter of the act).
- No hidden placeholders — only explicit `## Open Questions` sections for unresolved items.
- Continuity touchpoints are specific (named entities, facts, timeline constraints).
- Chapter summaries advance the act's dramatic function (no filler chapters).
- No forbidden vocabulary (delve, multifaceted, etc.).
