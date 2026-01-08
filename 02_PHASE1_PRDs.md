# Phase 1 MVP - Product Requirements Documents

## PRD 1.1: Story Bible Schema

### Overview
A structured set of markdown templates that serve as the single source of truth for all story facts, character details, and world rules. Every skill in the system references these documents to maintain consistency.

### Problem Statement
AI-assisted writing frequently produces inconsistencies because:
- Character details aren't centrally tracked
- World rules exist only in the writer's head
- Scene-to-scene continuity relies on fallible memory
- No single reference prevents contradictions

### User Stories

**US-1.1.1**: As a writer, I want a character profile template so that Claude has consistent information about each character's voice, history, and capabilities.

**US-1.1.2**: As a writer, I want a world rules document so that magic systems, technology limits, and geographic facts are enforced automatically.

**US-1.1.3**: As a writer, I want a scene tracker so that Claude knows what each character has learned, acquired, or experienced.

**US-1.1.4**: As a writer, I want the story bible to be human-readable markdown so I can edit it in any text editor.

### Functional Requirements

#### FR-1.1.1: Character Profile Template
Each character file (`characters/{name}.md`) must include:

```markdown
# {Character Name}

## Core Identity
- **Full Name**: 
- **Age**: 
- **Role in Story**: (protagonist, antagonist, supporting, minor)
- **POV Character**: (yes/no)

## Voice Profile
### Internal Voice
- **Worldview Filter**: How they interpret events (optimistic, cynical, analytical, emotional, etc.)
- **Internal Monologue Style**: (fragmented, flowing, self-critical, confident, etc.)
- **Key Concerns**: What occupies their thoughts

### External Voice (Dialogue)
- **Speech Patterns**: (formal, casual, clipped, verbose, etc.)
- **Vocabulary Level**: (educated, street-smart, technical, simple)
- **Verbal Tics**: Phrases they repeat, words they overuse
- **What They Avoid Saying**: Topics, words, or expressions they never use

### Voice Examples
<!-- Include 2-3 example passages that capture this character's voice -->

## Background
### Formative Events
<!-- Events that shaped their worldview -->

### Character Traits
- **Core personality traits**:
- **Social / interpersonal style**:
- **Moral / values-driven traits**:
- **Emotional tendencies**:
- **Intelligence / Thinking style**:
- **Work traits**:
- **Flaws**:
- **Under-pressure behaviors**:
- **Communication quirks**:

### Relationships
<!-- Key relationships and their nature -->

### Secrets
<!-- What they hide from others -->

## Physical
- **Appearance**: 
- **Distinguishing Features**:
- **Typical Dress**:

## Capabilities
- **Skills**:
- **Limitations**:
- **What They Cannot Do**: (important for consistency)

## Arc
- **Starting State**:
- **Core Wound/Want/Need**:
- **Ending State**: (if known)
```

#### FR-1.1.2: World Rules Document
`bible/world-rules.md` must include:

```markdown
# World Rules

## Setting
- **Time Period**:
- **Location(s)**:
- **Technology Level**:
- **Social Structure**:

## Geography
### Key Locations
<!-- Include spatial relationships (X is north of Y, Z takes 2 days travel from W) -->

### Geography Constraints
<!-- Mountains in Kansas = NO. List what does NOT exist. -->

## Magic/Technology System (if applicable)
### Rules
1. {Rule 1 - what IS possible}
2. {Rule 2}

### Limitations
1. {Limitation 1 - what is NOT possible}
2. {Limitation 2}

### Costs
<!-- What does using magic/technology cost? -->

## Social Rules
### Power Structures
### Cultural Norms
### What Is Forbidden

## Hard Constraints
<!-- List things that MUST NOT happen. These are non-negotiable. -->
1. 
2.
```

#### FR-1.1.3: Story Bible Core
`bible/story-bible.md` must include:

```markdown
# Story Bible: {Title}

## Premise
<!-- One-paragraph story summary -->

## Genre
- **Primary Genre**: 
- **Secondary Genre(s)**:

## Theme
- **Controlling Idea**: <!-- One sentence thesis the story argues -->
- **Thematic Question**: 

## Timeline
### Story Timeline
| Event | When | Who Involved | Consequences |
|-------|------|--------------|--------------|

### Backstory Timeline
<!-- Events before story begins -->

## Story Structure
### Beginning Hook
### Middle Build  
### Ending Payoff

## Obligatory Scenes (Genre-Specific)
<!-- List required scenes for your genre -->
```

#### FR-1.1.4: Scene Tracker
`bible/scene-tracker.md` must include:

```markdown
# Scene Tracker

## Scene Log

### Scene: {Scene ID/Name}
- **Chapter**: 
- **POV**: 
- **Characters Present**:
- **Location**:
- **Time**: 

#### What Happened
<!-- Brief summary -->

#### Character Knowledge Changes
| Character | Learned | Still Doesn't Know |
|-----------|---------|-------------------|

#### Object Tracking
| Character | Acquired | Lost/Used |
|-----------|----------|-----------|

#### Relationship Changes
| Relationship | Change |
|--------------|--------|

#### World State Changes
<!-- Any permanent changes to the world -->
```

### Non-Functional Requirements

- **NFR-1.1.1**: All templates must be valid markdown
- **NFR-1.1.2**: Templates must be readable without specialized tools
- **NFR-1.1.3**: Templates must support partial completion (not every field required)
- **NFR-1.1.4**: File naming must be URL-safe (lowercase, hyphens, no spaces)

### Acceptance Criteria
1. All four template types exist and are documented
2. Templates can be created by hand in any text editor
3. Templates include clear instructions/comments for each section
4. Empty templates don't break skills that reference them
5. Example templates provided for reference

---

## PRD 1.2: Scene Architect Skill

### Overview
A skill that transforms a rough scene idea or outline into a structured scene blueprint following Story Grid's Five Commandments of Storytelling.

### Problem Statement
Writers often start drafting without clear scene structure, leading to:
- Scenes that don't turn (no value shift)
- Missing or weak crises
- Unclear purpose for the scene
- Rambling prose without direction

### User Stories

**US-1.2.1**: As a writer, I want to input a rough scene idea and receive a structured blueprint so that my scene has proper dramatic structure.

**US-1.2.2**: As a writer, I want the blueprint to identify the specific value shift so I know what changes by scene's end.

**US-1.2.3**: As a writer, I want the blueprint to specify the crisis type so I can write a meaningful decision.

### Functional Requirements

#### FR-1.2.1: Input Requirements
The skill must accept:
- Scene description (free text, 50-500 words)
- POV character (references character file)
- Characters present (list)
- Scene's purpose in story (optional but recommended)
- Previous scene summary (optional, for continuity)

#### FR-1.2.2: Context Loading
Before generating blueprint, skill must read:
1. `bible/story-bible.md`
2. Character file for POV character
3. Character files for all present characters
4. `bible/scene-tracker.md` for continuity

#### FR-1.2.3: Output Blueprint Structure
```markdown
# Scene Blueprint: {Scene Name}

## Scene Metadata
- **POV Character**: 
- **Characters Present**:
- **Location**:
- **Time**:

## Scene Purpose
- **Story Function**: (advances plot / reveals character / reveals setting / reveals context)
- **Value at Stake**: (e.g., life/death, love/hate, freedom/captivity)
- **Opening Value**: (+/-) 
- **Closing Value**: (+/-)

## Five Commandments

### 1. Inciting Incident
- **Type**: (causal or coincidental)
- **Description**: 
- **What changes**: 

### 2. Progressive Complications
- **Complication 1**: 
- **Complication 2**:
- **Turning Point**: (the complication that forces the crisis)
- **Type**: (active or revelatory)

### 3. Crisis
- **Type**: (Best Bad Choice / Irreconcilable Goods)
- **Question**: {Character} must choose between {A} or {B}
- **Stakes of A**:
- **Stakes of B**:

### 4. Climax
- **Choice Made**: 
- **Action Taken**:

### 5. Resolution
- **Immediate Consequence**:
- **Value Shift Achieved**: from {X} to {Y}

## Scene Notes
### POV Character's Goal
### Obstacles
### Sensory Anchor (setting detail to ground scene)
### Key Props/Objects
```

#### FR-1.2.4: Validation
Blueprint must be validated for:
- Value shift exists (opening ≠ closing)
- Crisis is clear choice, not obvious answer
- Turning point exists and forces crisis
- Scene serves at least one story function

### Non-Functional Requirements
- **NFR-1.2.1**: Generation must complete in under 60 seconds
- **NFR-1.2.2**: Must handle incomplete input gracefully (ask clarifying questions)
- **NFR-1.2.3**: Must not hallucinate character details not in profiles

### Acceptance Criteria
1. Blueprint follows Five Commandments structure
2. Blueprint references only characters from input
3. Value shift is explicit and meaningful
4. Crisis presents genuine choice with stakes
5. Writer can modify blueprint before drafting

---

## PRD 1.3: Scene Drafter Skill

### Overview
A skill that transforms a scene blueprint into full prose draft while maintaining character voice, respecting world rules, and avoiding AI prose patterns.

### Problem Statement
AI-generated prose often:
- Loses character voice consistency
- Forgets what characters know or possess
- Violates established world rules
- Produces generic, detectable AI prose
- Uses uniform sentence structures

### User Stories

**US-1.3.1**: As a writer, I want my scene draft to match my POV character's established voice so the prose feels authentic.

**US-1.3.2**: As a writer, I want the draft to respect my world rules so magic/technology/geography are consistent.

**US-1.3.3**: As a writer, I want prose that doesn't read like AI-generated content so readers stay immersed.

**US-1.3.4**: As a writer, I want sensory details that go beyond visual so the scene feels embodied.

### Functional Requirements

#### FR-1.3.1: Context Loading (Mandatory)
Before drafting, must load:
1. Scene blueprint (required)
2. `bible/story-bible.md`
3. POV character profile (voice section critical)
4. All present character profiles  
5. `bible/world-rules.md`
6. `bible/scene-tracker.md` (recent entries)

#### FR-1.3.2: Voice Enforcement
Draft must adhere to POV character's voice profile:
- Internal monologue matches "Internal Voice" specification
- Worldview filter colors all observations
- Vocabulary matches character's level
- Sentence rhythm matches character's pattern

#### FR-1.3.3: World Rule Enforcement
During drafting, must check:
- Geographic facts (no mountains in Kansas)
- Technology/magic system rules
- Timeline consistency
- Character knowledge (what they know vs. don't know)

#### FR-1.3.4: Anti-AI Prose Requirements
Draft must NOT include:
- Overused AI vocabulary: delve, multifaceted, navigate, foster, embark, journey, landscape, testament, unwavering, intricate, beacon, realm, pivotal, nuance, crucial, indispensable, comprehensive, furthermore, consequently, hence, vital
- Generic descriptions where specific details would work
- Uniform sentence lengths (must vary)
- Excessive hedging language
- Generic character names (Emily, Sarah, John, etc.) unless in character profiles

Draft MUST include:
- At least 2 non-visual sensory details (sound, smell, touch, taste)
- At least 1 specific concrete detail (not generic)
- Sentence length variety (short, medium, long mix)
- Character-specific observations/reactions

#### FR-1.3.5: Output Format
```markdown
# Scene Draft: {Scene Name}

---

{Prose content}

---

## Draft Metadata
- **Word Count**: 
- **POV Character**: 
- **Value Shift**: {from} → {to}
- **Files Referenced**:
  - {list of bible/character files used}
```

### Non-Functional Requirements
- **NFR-1.3.1**: Draft generation must complete in under 3 minutes
- **NFR-1.3.2**: Draft must be self-contained (readable without blueprint)
- **NFR-1.3.3**: Must flag any ambiguities rather than hallucinate

### Acceptance Criteria
1. Draft follows blueprint structure
2. POV character voice matches profile
3. No world rule violations
4. Contains required sensory variety
5. Passes basic AI vocabulary check
6. Sentence length varies measurably

---

## PRD 1.4: Character Truth Pass

### Overview
A revision skill that audits a scene draft for character consistency, checking voice, knowledge, and behavior against established profiles.

### Problem Statement
Even well-structured drafts can drift from established character truth:
- Voice shifts mid-scene
- Characters know things they shouldn't
- Actions contradict established motivations
- Dialogue patterns become inconsistent

### User Stories

**US-1.4.1**: As a writer, I want to know if my POV character's voice drifted so I can correct it.

**US-1.4.2**: As a writer, I want to catch knowledge violations so characters don't reveal things they can't know.

**US-1.4.3**: As a writer, I want dialogue flagged when it doesn't match character patterns so I can revise.

### Functional Requirements

#### FR-1.4.1: Input Requirements
- Scene draft (required)
- Character profiles for all characters in scene (required)
- Scene tracker (for knowledge verification)

#### FR-1.4.2: Checks Performed

**Voice Consistency**
- Does internal monologue match POV profile throughout?
- Are observations filtered through character's worldview?
- Is vocabulary consistent with character's level?
- Any jarring voice shifts?

**Knowledge Verification**
- Does character reference information they couldn't have?
- Are they missing information they should have?
- Any anachronistic knowledge?

**Dialogue Consistency**  
- Does each character's speech match their profile?
- Are verbal tics present where expected?
- Any out-of-character statements?

**Behavioral Consistency**
- Do actions align with established motivations?
- Any decisions that contradict character profile?
- Are capabilities respected (no sudden new skills)?

#### FR-1.4.3: Output Format
```markdown
# Character Truth Audit: {Scene Name}

## Summary
- **Issues Found**: {count}
- **Severity**: (high/medium/low)

## Voice Consistency

### POV Character: {Name}
{Assessment}

**Issues:**
- **Line/Para**: "{excerpt}"
  - **Problem**: {description}
  - **Profile Reference**: {what profile says}
  - **Suggested Fix**: {recommendation}

## Knowledge Verification

### {Character Name}
**Issues:**
- **Line**: "{excerpt}"  
  - **Problem**: Character knows {X} but shouldn't because {reason}
  - **Fix**: {recommendation}

## Dialogue Consistency

### {Character Name}
**Issues:**
- **Line**: "{dialogue excerpt}"
  - **Problem**: {description}
  - **Profile says**: {speech pattern reference}
  - **Suggested revision**: "{alternative}"

## Behavioral Consistency

### {Character Name}
**Issues:**
- **Action**: "{action excerpt}"
  - **Problem**: {description}
  - **Profile says**: {motivation/capability reference}
  - **Suggested Fix**: {recommendation}

## Clean Passes
<!-- What was checked and found consistent -->
```

### Non-Functional Requirements
- **NFR-1.4.1**: Audit must complete in under 2 minutes
- **NFR-1.4.2**: Must cite specific lines, not general complaints
- **NFR-1.4.3**: Must reference profile sections to justify flags

### Acceptance Criteria
1. All present characters are audited
2. Issues cite specific text locations
3. Issues reference specific profile sections
4. Suggestions are actionable (not just "fix this")
5. False positive rate under 20%

---

## PRD 1.5: Basic Pipeline Runner

### Overview
An orchestration command that runs skills in sequence with human review pauses between each step.

### Problem Statement
Running skills manually requires:
- Remembering the correct order
- Manually passing outputs to inputs
- Tracking what step you're on
- Restarting from the right point after breaks

### User Stories

**US-1.5.1**: As a writer, I want to start a pipeline on a scene and have it guide me through each step.

**US-1.5.2**: As a writer, I want to pause between steps to review and edit before continuing.

**US-1.5.3**: As a writer, I want to resume a pipeline after taking a break.

**US-1.5.4**: As a writer, I want to skip steps or run individual steps if needed.

### Functional Requirements

#### FR-1.5.1: Pipeline Stages
```
Stage 1: Scene Architect → blueprint.md
         ↓ [PAUSE: Review blueprint, edit if needed]
Stage 2: Scene Drafter → draft.md  
         ↓ [PAUSE: Review draft, edit if needed]
Stage 3: Character Truth → audit.md
         ↓ [PAUSE: Review issues, apply fixes]
         [COMPLETE]
```

#### FR-1.5.2: State Tracking
Create `.pipeline-state` file in scene directory:
```yaml
scene: {scene-directory}
current_stage: 2
started: 2026-01-08T10:30:00Z
last_updated: 2026-01-08T11:15:00Z
stages:
  1:
    status: complete
    output: blueprint.md
    completed: 2026-01-08T10:45:00Z
  2:
    status: in_progress
    output: draft.md
  3:
    status: pending
```

#### FR-1.5.3: Commands

**Start Pipeline**
```bash
claude /project:pipeline-run chapters/ch01/scene-01/
```
- Creates scene directory if needed
- Prompts for scene input if not present
- Runs Stage 1
- Saves state

**Continue Pipeline**
```bash
claude /project:pipeline-run chapters/ch01/scene-01/
```
- Reads state file
- Runs next stage
- Updates state

**Run Specific Stage**
```bash
claude /project:skills:scene-architect chapters/ch01/scene-01/
claude /project:skills:scene-draft chapters/ch01/scene-01/
claude /project:skills:character-truth chapters/ch01/scene-01/
```

#### FR-1.5.4: Pause Behavior
After each stage:
1. Save output file
2. Update state file
3. Report completion
4. Provide guidance: "Review {output}, edit if needed, then run `/project:pipeline-run` to continue"

### Non-Functional Requirements
- **NFR-1.5.1**: State file must survive Claude session restarts
- **NFR-1.5.2**: Pipeline must handle missing files gracefully
- **NFR-1.5.3**: Must support Git commits between stages

### Acceptance Criteria
1. Pipeline runs all three stages in order
2. Pauses after each stage for review
3. State persists between sessions
4. Can resume from any stage
5. Individual skills work independently

---

## Appendix: Skill Definitions (YAML Format)

For reference, skills will be defined in YAML with this structure:

```yaml
name: scene-architect
version: 1.0.0
description: Transform scene idea into structured blueprint

inputs:
  required:
    - scene_description
    - pov_character
    - characters_present
  optional:
    - scene_purpose
    - previous_scene

context:
  always_load:
    - bible/story-bible.md
    - bible/scene-tracker.md
  load_for_characters:
    - characters/{character}.md

output:
  format: markdown
  template: scene-blueprint
  location: "{scene_directory}/blueprint.md"

validation:
  - value_shift_exists
  - crisis_is_choice
  - turning_point_exists
```

This YAML structure allows skills to be:
- Version controlled
- Self-documenting
- Machine-parseable
- Extensible
