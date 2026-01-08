# Fiction Writing Skills System - Product Roadmap

## Executive Summary

This product roadmap defines a Claude Code-powered fiction writing assistant system built on research-informed craft principles from Story Grid methodology, Stephen King's "On Writing," and professional editorial workflows.

**Primary User**: Fiction writers using Claude Code CLI to draft, revise, and polish short stories, novellas, and novels.

**Core Problem**: AI-assisted scene drafting frequently loses character voice consistency, forgets continuity details (what characters know, possess, or have experienced), violates world rules (magic systems, geography, technology constraints), and produces prose with detectable AI patterns (generic descriptions, uniform sentence structure, overused vocabulary).

**Solution**: A hybrid system of skills, commands, and agents that enforces craft principles at every stage of scene development while maintaining human creative control.

---

## Research Foundation

### Story Grid Methodology (Shawn Coyne)
- **Five Commandments**: Every scene must have an Inciting Incident, Progressive Complication (Turning Point), Crisis, Climax, and Resolution
- **Value Shift**: Every scene must change a value (positive to negative or vice versa)
- **Scene Purpose**: Each scene must reveal character, reveal setting, reveal context, OR advance plot (ideally 2+)
- **Hierarchy**: Global Story → Acts → Sequences → Scenes → Beats

### Stephen King's "On Writing"
- **Paragraph as unit**: Build scene paragraph by paragraph
- **Show don't tell**: Avoid adverbs, use active voice
- **Natural dialogue**: Use your own vocabulary, not thesaurus words
- **Kill your darlings**: Cut 10%+ in revision
- **Specificity**: Concrete details over generic descriptions

### Character Voice Craft
- **Voice = worldview filter**: How characters interpret and respond to events internally
- **Backstory creates voice**: Past trauma/joy shapes present perception
- **Consistency builds trust**: Characters shouldn't suddenly change voice
- **Subtext matters**: What's NOT said is as important as dialogue
- **Differentiation**: Syntax, rhythm, word choice, recurring patterns

### AI Prose Weaknesses (To Counter)
- Over-consistency (too polished, uniform sentence lengths)
- Regression to mean (generic positive descriptions vs. specific facts)
- Overused vocabulary ("delve," "multifaceted," "navigate," "foster")
- Vagueness (avoids concrete details, specific examples)
- Generic names ("Emily," "Sarah" appear 60-70% of time)
- Lacks personal experience/unique perspective
- Smooth but shallow (missing "deeper web of associations")

---

## Phase 1: MVP (Minimal Viable Product)

### Timeline: 2-3 weeks to functional prototype

### Goal
Enable a writer to transform a scene outline or rough draft into a polished short story scene with:
- Consistent character voice
- Enforced world rules
- Proper scene structure
- Human-sounding prose

### Features

#### 1.1 Story Bible Schema (Foundation)
**Deliverable**: Structured markdown templates for:
- `story-bible.md` - Core story rules, timeline, world facts
- `characters/*.md` - Character profiles with voice guides
- `world-rules.md` - Magic systems, technology, geography constraints
- `scene-tracker.md` - What happened, what characters know

**Why MVP**: Every other feature depends on having structured context to reference.

#### 1.2 Scene Architect Skill
**Deliverable**: `/project:skills:scene-architect` command

**Function**: Takes scene outline/rough idea → generates structured scene plan following Story Grid Five Commandments:
1. Identifies Inciting Incident
2. Maps Progressive Complications
3. Defines Crisis (Best Bad Choice or Irreconcilable Goods)
4. Plans Climax
5. Specifies Resolution and Value Shift

**Inputs Required**:
- Scene outline or rough description
- POV character
- Present characters
- Scene goal/purpose in story

**Output**: Scene blueprint markdown file

#### 1.3 Scene Drafter Skill  
**Deliverable**: `/project:skills:scene-draft` command

**Function**: Takes scene blueprint → generates full prose draft

**Context Loading**:
1. Reads story bible
2. Reads all present character profiles
3. Reads relevant world rules
4. Checks scene tracker for continuity

**Draft Requirements**:
- Follows scene blueprint structure
- Uses character-appropriate voice for POV
- Respects world rules
- Includes sensory details (not just visual)
- Varies sentence length and structure
- Avoids AI vocabulary list

**Output**: Scene draft markdown file

#### 1.4 Character Truth Pass
**Deliverable**: `/project:skills:character-truth` command

**Function**: Reviews draft for character consistency

**Checks**:
- Does POV character's internal voice match their profile?
- Are dialogue patterns consistent with each character?
- Do characters know only what they should know?
- Do character actions align with established motivations?
- Are character-specific speech patterns preserved?

**Output**: Annotated draft with issues + suggested fixes

#### 1.5 Basic Pipeline Runner
**Deliverable**: `/project:pipeline-run` command

**Function**: Orchestrates skills in sequence with pause for review

**Flow**:
```
scene-architect → [PAUSE: review blueprint]
scene-draft → [PAUSE: review draft]  
character-truth → [PAUSE: review/accept fixes]
```

**State Tracking**: `.pipeline-state` file in scene directory

### MVP Success Criteria
1. Writer can produce a complete short story scene from outline in under 2 hours
2. Character voice remains consistent across multiple scenes
3. No world rule violations in generated content
4. Prose passes "gut check" for human-sounding quality
5. Writer maintains creative control at each stage

### MVP Exclusions (Deferred to Phase 2+)
- Full agent architecture
- Dialogue subtext analysis
- Line-level tightening
- AI detection/humanization pass
- Multi-scene continuity tracking
- Tension curve analysis
- Callbacks and foreshadowing

---

## Phase 2: Feature Expansion

### Timeline: 4-6 weeks after Phase 1 completion

### Goal
Add depth to revision process and introduce agent-based diagnosis

### Features

#### 2.1 Scene Director Agent
**Function**: Assesses what a scene needs rather than running all passes

**Capabilities**:
- Diagnose scene problems
- Recommend specific skills to apply
- Track scene history and evolution
- Spawn specialist subagents

#### 2.2 Prose Surgeon Subagent
**Function**: Line-level craft improvements

**Capabilities**:
- Sentence rhythm analysis
- Word choice refinement
- Adverb elimination
- Passive voice → active voice conversion
- Redundancy removal
- "Kill your darlings" suggestions

#### 2.3 Dialogue Subtext Pass
**Deliverable**: `/project:skills:dialogue-subtext` command

**Function**: Analyzes dialogue for:
- Is subtext present? (What's NOT said)
- Are characters speaking too directly?
- Does dialogue serve multiple purposes?
- Are action beats meaningful?

#### 2.4 Tension Curve Analysis
**Deliverable**: `/project:skills:tension-curve` command

**Function**: Maps tension through scene
- Identifies flat spots
- Suggests complication injection points
- Validates rising action to climax

#### 2.5 AI Humanization Pass
**Deliverable**: `/project:skills:humanize` command

**Function**: Detects and fixes AI prose patterns
- Flags overused AI vocabulary
- Identifies too-uniform sentence structure  
- Adds specific concrete details to replace generic descriptions
- Introduces controlled imperfection
- Validates sensory variety

#### 2.6 Continuity Keeper Subagent
**Function**: Cross-references all story documents

**Capabilities**:
- Track character knowledge state
- Validate timeline consistency
- Check geographic/spatial logic
- Verify object tracking (what's in pockets, hands, etc.)
- Flag magic system violations

### Phase 2 Success Criteria
1. Scene Director accurately diagnoses problems 80%+ of time
2. Prose Surgeon reduces line-edit time by 50%
3. Continuity errors caught before manual review
4. Writers report improved dialogue depth

---

## Phase 3: Advanced Features & Polish

### Timeline: Ongoing refinement (6+ months)

### Goal
Scale to novels, add sophisticated analysis, enable sharing

### Features (Placeholder - to be defined after Phase 2 feedback)

#### 3.1 Multi-Scene Arc Tracking
- Chapter-level tension management
- Character arc progression
- Theme reinforcement tracking

#### 3.2 Voice Fingerprinting
- Learn specific author's style
- Generate prose matching author voice
- Distinguish between characters automatically

#### 3.3 Comparative Analysis
- Compare scene to masterwork examples
- Genre convention checking
- Obligatory scene verification

#### 3.4 Collaboration Features
- Export/import story bibles
- Share skill configurations
- Community skill library

#### 3.5 Genre-Specific Modules
- Thriller pacing requirements
- Romance beat sheet integration
- Mystery clue planting/revelation
- Science fiction consistency checking
- Historical fiction accuracy validation

---

## Customer Feedback Touchpoints

### Post-Phase 1 Interview Questions
1. What's working well in the pipeline?
2. Where do you find yourself fighting the system?
3. Are the story bible templates capturing what you need?
4. How accurate is character voice preservation?
5. What's missing that would save you the most time?
6. Rate prose quality 1-10 before your edits
7. What manual steps are you still doing that feel automatable?

### Post-Phase 2 Interview Questions
1. How accurate is Scene Director's diagnosis?
2. Is the Prose Surgeon helping or getting in the way?
3. Are continuity errors being caught reliably?
4. How has dialogue depth changed?
5. What's your new bottleneck?
6. Ready to try a novella/novel with this system?

### Metrics to Track
- Time from outline to polished scene
- Number of manual revision passes needed
- Character voice consistency (self-rated)
- World rule violations caught vs. missed
- User satisfaction with prose quality
- Feature usage frequency

---

## Technical Dependencies

### Required
- Claude Code CLI
- Git (version control)
- Markdown editor
- File system access

### Recommended
- VS Code or similar IDE
- GitHub for backup/collaboration
- Obsidian or similar for story bible navigation

---

## Risk Assessment

### High Risk
- **Scope creep**: Novel-length projects before short story workflow is solid
- **Over-automation**: Removing writer judgment from creative decisions
- **Context limits**: Story bible + characters + scene may exceed context window

### Mitigation Strategies
- Enforce short story focus in MVP
- All skills pause for human review by default
- Design modular context loading (only load relevant characters)
- Implement summarization for large story bibles

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-01-08 | Initial roadmap based on research |
