# Evaluation: Entity-Relationship Matrix + Platform Choice

## The Matrix: Blunt Assessment

### What's Good About It

The concept is sound. It captures the right thing — **who knows/has/wants what about whom** — which is exactly what the continuity agent needs. The LOTR example shows it works intuitively for a human reader. The append-only rule ("don't replace, add") is correct for story continuity where history matters.

### Problem 1: Markdown Tables Don't Scale

A novel with 8 characters, 5 locations, 10 objects, and 5 facts = **28 entities**. That's a 28×28 matrix = **784 cells**. In markdown, that's unreadable and uneditable:

```
| From / About | Marcus | Elena | Kai | Zone1 | Zone2 | Zone3 | Prosthetic | Signal | ... (28 columns)
```

No human or AI can visually parse a 28-column markdown table. The LOTR example works because it has 7 entities. Most novels would have 20-50+.

**Verdict**: The format breaks at realistic story scale.

### Problem 2: Cell Content Bloat

With append-only, cells accumulate:

```
| Gollum → Ring | lost, covets, calls "my precious", 
                  followed Bilbo for, nearly recovered in 
                  cave, tracked to Shire, followed Fellowship, 
                  ambushed Frodo on stairs, bit off finger, 
                  fell into Mount Doom with |
```

After 30 chapters, high-traffic cells become paragraphs. The matrix stops being a matrix and becomes a wall of text with table formatting.

**Verdict**: Append-only in a fixed-width cell format is unsustainable.

### Problem 3: No Temporal Ordering

The current format has no timestamps or scene references in the cells:

```
| Frodo → Ring | lost |
```

*When* did Frodo lose the Ring? Chapter 1? Chapter 30? This matters enormously for continuity — if I'm writing Chapter 15, I need to know what's true *at that point*, not the full history dump.

**Verdict**: The matrix tells you the full relationship history but can't answer "what does Frodo have in Chapter 12?"

### Problem 4: Not Machine-Queryable

The continuity agent needs to answer: "Does Marcus know about Elena's sign language in Act 2?" With a markdown table, the only way to check is:

1. Load the entire matrix into context
2. Find the Marcus↔Elena cell
3. Parse the free-text contents
4. Determine if "knows sign language" appears

You proposed using grep/scripts to avoid loading full canon. But a markdown table defeats grep because the data isn't on its own line — it's embedded in a cell in a row with other cells. Grep can find "sign language" in the file, but can't tell you it's in the Marcus→Elena cell vs. the Elena→Elena cell.

**Verdict**: The format works for human reading but fights machine querying — which is the main use case for the continuity agent.

### Problem 5: Column Management

Every new entity requires adding a column to every existing row and a new row. In markdown, this means reformatting the entire table. If two branches of work add entities independently (say, Act 1 introduces "Zone Guard" and Act 2 introduces "Zone Map"), merging them requires restructuring the whole matrix.

**Verdict**: Structural fragility under concurrent or branching work.

### Problem 6: One Matrix or Many?

A single matrix for the whole novel = Problem 1 (too big). A matrix per act = continuity gaps between acts. A matrix per chapter = defeats the purpose.

**Verdict**: No good granularity choice with a flat table format.

---

## Proposed Fix: Keep the Concept, Change the Format

The **relationship-centric thinking** is right. The **markdown table** is the problem. Here's what I'd replace it with:

### Option A: Structured YAML (Machine-First, Human-Readable)

```yaml
# canon/relationships.yaml

entities:
  marcus:
    type: character
    introduced: L1/concept
    
  elena:
    type: character
    introduced: L1/concept

  zone-3:
    type: location
    introduced: L1/concept

  prosthetic:
    type: object
    introduced: L1/concept

relationships:
  - from: marcus
    to: elena
    rel: distrusts
    context: "refuses her help at Zone perimeter"
    established: Act1/Ch1
    status: active

  - from: marcus
    to: elena
    rel: reluctant_alliance
    context: "agrees to let Elena navigate after first failure"
    established: Act1/Ch4
    status: active     # supersedes "distrusts" — both kept

  - from: marcus
    to: prosthetic
    rel: depends_on
    context: "lost leg in military service, prosthetic is part of identity"
    established: L1/concept
    status: active

  - from: marcus
    to: zone-3
    rel: cannot_enter
    context: "zones reject inorganic material"
    established: L1/concept
    status: active

  - from: elena
    to: zone-3
    rel: can_navigate
    context: "knows the zone paths, reason unknown"
    established: Act1/Ch2
    status: active

  - from: gollum
    to: ring
    rel: possessed
    context: "held for 500 years in Misty Mountains"
    established: backstory
    status: ended       # ← status tracking!

  - from: gollum
    to: ring
    rel: lost_to
    context: "Bilbo found ring during riddle game"
    established: backstory
    status: active
```

**Why this is better**:

| Problem | Markdown Table | YAML |
|---------|---------------|------|
| Scale | Breaks at 20+ entities | Flat list, scales to hundreds |
| Cell bloat | Paragraph-length cells | Each relationship is a separate entry |
| Temporal ordering | No timestamps | `established:` field with Act/Ch reference |
| Machine queryable | Grep can't isolate cells | `grep "from: marcus" -A4` gets full relationship |
| Column management | Restructure whole table | Just add an entry |
| Status tracking | Can't tell current vs. historical | `status: active/ended/superseded` |

### Querying the YAML

The continuity agent can now do targeted lookups:

```bash
# "What does Marcus know/have in Act 2?"
grep -A4 "from: marcus" canon/relationships.yaml | grep "status: active"

# "Who has a relationship with Zone 3?"
grep -B1 -A4 "to: zone-3" canon/relationships.yaml

# "What changed in Act 1 Chapter 4?"
grep -B2 -A3 "established: Act1/Ch4" canon/relationships.yaml
```

Or with a simple Python helper:

```python
def query_relationships(entity, as_of=None, status="active"):
    """Return all active relationships involving entity,
    optionally filtered to those established before a given point."""
    rels = yaml.safe_load(open('canon/relationships.yaml'))
    return [r for r in rels['relationships']
            if (r['from'] == entity or r['to'] == entity)
            and r['status'] == status
            and (as_of is None or r['established'] <= as_of)]
```

### Option B: Keep a Human-Readable Matrix View (Generated)

If you value the visual matrix for human review, **generate it from the YAML** — don't maintain it by hand:

```python
def render_matrix(relationships_yaml, as_of=None):
    """Generate a markdown matrix view from YAML source."""
    # Filter to active relationships at `as_of` point
    # Build entity × entity grid
    # Fill cells from relationship entries
    # Output markdown table
```

This gives you:
- **YAML** = source of truth (machine-queryable, scalable)
- **Markdown matrix** = generated view (human-scannable, disposable)
- Matrix can be regenerated at any time, filtered to any point in the story

---

## Mode A Continuity Rule (Updated)

```
IF changes_made_by == HUMAN:
    continuity_check = ON_REQUEST_ONLY
    
IF changes_made_by == AI (skill, agent, or other):
    continuity_check = AUTOMATIC
    # Continuity agent validates AI changes before commit
    # Human sees the report and approves/rejects
```

This is clean and respects the principle: trust the human's intentional changes, verify the AI's.

---

## Platform Question: Blunt Answer

### Does Antigravity "Simulate" Skills?

**Yes, that is essentially correct.** Here's what happens:

When Antigravity (or any IDE-integrated AI assistant) encounters a reference to a SKILL.md file, it:

1. **Reads** the SKILL.md contents into its context
2. **Interprets** the instructions as guidelines for its response
3. **Generates** output that attempts to follow those guidelines

But it does **not**:
- Execute the skill as a distinct, isolated process
- Enforce the skill's constraints as hard rules
- Track pipeline state across invocations
- Run multiple agents in parallel
- Guarantee faithful adherence to every instruction in the skill definition

The "simulation" problem you've observed — where the output doesn't strictly follow the SKILL.md — happens because the skill instructions compete with the model's general tendencies, conversation context, and system prompt. There's no enforcement layer.

### What About Multi-Agent?

Antigravity (this tool) runs as a **single agent with sequential tool calls**. It cannot:
- Spawn parallel agent processes
- Route different agents to different models
- Maintain separate context windows for sidecar agents (like our Continuity Agent design)
- Execute the MOE Mob pattern with true concurrent agents

It can *simulate* multi-agent by role-switching within a single context ("Now I'm the Plot Analyst... now I'm the Character Specialist..."), but this is exactly the simulation problem you identified — it's not faithful to separate agent definitions, and agents "bleed" into each other because they share context.

### Recommended Platform

| Platform | Mode A (Manual) | Mode C (MOE Mob) | Multi-Agent | Skill Fidelity | Tool Use |
|----------|-----------------|-------------------|-------------|----------------|----------|
| **Antigravity IDE** | ⚠️ Simulates | ❌ Can't do real MOE | ❌ Single agent | ⚠️ Approximate | ✅ Strong |
| **Claude Code CLI** | ✅ Runs skills faithfully | ⚠️ Sequential role-switch | ⚠️ Can orchestrate via scripts | ✅ Loads and follows SKILL.md | ✅ Strong |
| **Claude Code CLI + Python orchestrator** | ✅ | ✅ Real MOE possible | ✅ Via subprocess/API | ✅ | ✅ |
| **Gemini CLI** | ✅ Similar to Claude CLI | ⚠️ Same limitations | ⚠️ Same | ⚠️ Less tested with .claude/skills format | ✅ |
| **Codex CLI (OpenAI)** | ✅ | ⚠️ Same | ⚠️ Same | ⚠️ Different skill format needed | ✅ |

### Recommendation: Claude Code CLI + Orchestration Script

**Primary platform**: Claude Code CLI — it natively reads `.claude/skills/*/SKILL.md` files, follows them more faithfully than IDE integration, and supports tool use (file read/write, command execution).

**For MOE Mob**: A Python or Bash orchestration script that:
1. Calls Claude API with each agent's role as the system prompt
2. Passes the current artifact + context manifest
3. Collects each agent's comment
4. Presents comments to the human one at a time in the CLI
5. Handles the back-and-forth

```python
# Simplified orchestrator concept
def run_mob_session(artifact, manifest, agents):
    for agent in agents:
        if not agent.active_at_level(manifest.level):
            continue
        # Call Claude API with agent-specific system prompt
        comment = call_claude(
            model=agent.model_tier,
            system=agent.system_prompt,
            context=load_manifest_files(manifest),
            user=f"Review this artifact:\n{artifact}"
        )
        # Present to human
        print(f"\n[{agent.name}]: {comment}")
        response = input("Your response: ")
        # Handle back-and-forth...
```

**For Continuity Agent**: A separate Haiku/Flash call + grep scripts, invoked by the orchestrator, not in the main conversation.

### What Antigravity IS Good For

- **Viewing and editing canon files** (it's an IDE, files are its strength)
- **Reviewing generated artifacts** before commit
- **Quick Mode A validation** where strict skill adherence isn't critical
- **Design discussions** like the one we're having right now

So the workflow might be:
- **Design and plan** in Antigravity (you're already doing this)
- **Execute pipeline steps** via Claude Code CLI + orchestrator
- **Review results** back in Antigravity or your preferred editor
