---
name: Tension Curve
description: Map the micro-tension beats within a chapter to ensure escalation, release, and sustained dread or anticipation.
---

# Tension Curve Skill

Map the micro-tension beats within a chapter to ensure escalation, release, and sustained dread or anticipation.

## Usage
```
/project:skills:tension-curve {chapter_promise}
```

## Process

### Inputs
- **Required**: `chapter_promise`
- **Optional**: `beats_per_chapter` (default: 5)

### Steps
1. Plot entries: where does the pressure start?
2. Plot complications: what increases the social/physical/moral stakes?
3. Identify the Peak (the highest tension point).
4. Identify the Twist/Cost: what is lost at the peak?
5. Plot the Exit: where does the tension settle (usually higher than it started)?
6. Generate a visualization map (markdown table or list).

## Output Format
- Tension Map Table: [Beat | Tension Level (1-10) | Description]
- Peak Tension description
- Twist/Cost description

## Quality Checks
- Tension does not plateau for more than two beats.
- The Peak occurs in the final 30% of the chapter.
- Pacing reflects the genre rhythm (e.g., sharp jumps for thriller).
