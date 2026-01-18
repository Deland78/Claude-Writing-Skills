---
name: AI Filter Humanize
description: Remove AI fingerprints and add human texture - specificity, imperfection, controlled unpredictability, and subtle sensory detail.
---

# AI Filter Humanize Skill

Remove AI fingerprints and add human texture: specificity, imperfection, controlled unpredictability, and subtle sensory detail.

## Usage
```
/project:skills:ai-filter-humanize {chapter_draft}
```

## Process

### Inputs
- **Required**: `chapter_draft`

### Steps
1. Remove generic phrases: "in that moment", "it seemed", "little did he know", etc.
2. Reduce symmetry and perfect logic in dialogue and actions.
3. Add small human flaws: hesitation, misreading, irritation, awkward timing.
4. Insert at most 3 vivid specific details that feel observed, not invented.
5. Ensure one hard line per ~800-1200 words (punch line).

## Output Format
- Humanized chapter draft
- List of removed AI tells

## Quality Checks
- No over-smoothing; keep edges.
- Added details feel physically plausible.
- [ ] Zero instances of forbidden words or phrases.

## Forbidden Vocabulary

### Words
delve, multifaceted, navigate, foster, embark, journey, landscape, testament, unwavering, intricate, beacon, realm, pivotal, nuance, crucial, indispensable, comprehensive, furthermore, consequently, hence, vital, commendable, meticulous, endeavor, profound, intriguing, leverage, facet, compelling, cohesive, streamline, enhance

### Phrases
"little did * know", "as * continued", "in this moment", "in this day and age", "a testament to", "it's important to note", "is not just *, it's", "the * tapestry of", "nestled in", "a symphony of", "dance of", "serves as a"
