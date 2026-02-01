---
description: Skill evolution system - analyze, evaluate, and evolve skills
---

# Darwin - Skill Evolution System

Darwin monitors, evaluates, and evolves your Claude Code skills over time.

## Commands

**Usage:** `/darwin [command]`

| Command | Description |
|---------|-------------|
| `status` | Dashboard with fitness scores for all skills (default) |
| `evaluate [skill]` | Deep analysis of a specific skill |
| `evolve` | Run evolution cycle (suggest + apply mutations) |
| `suggest` | Show mutation suggestions without applying |
| `telemetry` | View raw recent telemetry events |
| `compile [skill]` | Recompile skill from modules |

If no command provided, run `status`.

---

## Evolution Commands

### Command: `evolve`

Run the evolution engine to improve underperforming skills.

```bash
python3 ~/.claude/darwin/bin/evolve.py cycle
```

This will:
1. **EVALUATE** - Score all skills by fitness
2. **SNAPSHOT** - Save weekly evaluation for trend tracking
3. **EVOLVE** - Apply mutations to underperforming skills

### Command: `suggest`

Show what mutations would be applied without changing anything.

```bash
python3 ~/.claude/darwin/bin/evolve.py suggest
```

### Command: `compile [skill]`

Recompile a skill from its module definition.

```bash
python3 ~/.claude/darwin/bin/compile.py [skill]
# or for all skills:
python3 ~/.claude/darwin/bin/compile.py --all
```

---

## Implementation

### Parse Command

```
COMMAND = first word of $ARGUMENTS (default: "status")
SKILL_ARG = second word of $ARGUMENTS (for evaluate)
```

---

### Command: `status`

**Step 1:** Run the evaluation script
```bash
~/.claude/darwin/bin/evaluate.sh
```

**Step 2:** Parse the JSON output and format as dashboard.

**Step 3:** Output format:

```
═══════════════════════════════════════════════════
DARWIN SKILL STATUS
═══════════════════════════════════════════════════

DATA: [total] skill invocations │ Since: [date]

SKILL RANKINGS (by fitness)
───────────────────────────────────────────────────
 1. /[skill]     [bar]  [score]  [[count] uses]
 2. /[skill]     [bar]  [score]  [[count] uses]
 ...

METRICS BREAKDOWN
───────────────────────────────────────────────────
           Adopt  Complete  Efficient  Trend
[skill]    0.XX    0.XX      0.XX      0.XX
...

INSIGHTS
───────────────────────────────────────────────────
- Most used: /[skill] ([count]x)
- Unused: /[skills with 0 invocations]
- Top performer: /[highest fitness]

═══════════════════════════════════════════════════
```

**Bar chart helper:**
- 0.0-0.1: `░░░░░░░░░░`
- 0.1-0.2: `█░░░░░░░░░`
- 0.2-0.3: `██░░░░░░░░`
- ... up to 1.0: `██████████`

---

### Command: `evaluate [skill]`

**Step 1:** Run evaluation script and filter for specific skill.

**Step 2:** Read the skill file from `~/.claude/commands/[skill].md`

**Step 3:** Analyze skill structure:
- Has description in frontmatter? ✓/✗
- Has output format defined? ✓/✗
- Has examples? ✓/✗
- Has clear steps? ✓/✗
- Line count

**Step 4:** Output format:

```
═══════════════════════════════════════════════════
SKILL EVALUATION: /[skill]
═══════════════════════════════════════════════════

FILE: ~/.claude/commands/[skill].md
LINES: [count]

USAGE METRICS (Last 7 Days)
───────────────────────────────────────────────────
Invocations: [count]
Avg tools per invocation: [count]
Completion rate: [percent]%

FITNESS BREAKDOWN
───────────────────────────────────────────────────
Adoption:    [bar]  [score]  (% of total usage)
Completion:  [bar]  [score]  (% completed)
Efficiency:  [bar]  [score]  (inverse of tool count)
Trend:       [bar]  [score]  (week-over-week)
─────────────────────────────
TOTAL:       [bar]  [score]

STRUCTURE ANALYSIS
───────────────────────────────────────────────────
[✓] Has description in frontmatter
[✓] Has output format defined
[✗] Missing examples
[✓] Has implementation steps

RECOMMENDATIONS
───────────────────────────────────────────────────
1. [If low adoption] Skill is underused - consider if it's needed
2. [If low completion] Users abandon this skill - simplify output
3. [If low efficiency] Uses too many tools - streamline process
4. [If missing structure] Add examples, clearer output format

═══════════════════════════════════════════════════
```

---

### Command: `telemetry`

**Step 1:** Read last 20 lines from each telemetry file:
```bash
tail -10 ~/.claude/darwin/telemetry/skills.jsonl
tail -10 ~/.claude/darwin/telemetry/session_summaries.jsonl
```

**Step 2:** Format as readable table:

```
═══════════════════════════════════════════════════
DARWIN TELEMETRY (Recent Events)
═══════════════════════════════════════════════════

SKILL INVOCATIONS
───────────────────────────────────────────────────
[timestamp]  [session]  /[skill]  "[prompt preview]"
...

SESSION SUMMARIES
───────────────────────────────────────────────────
[timestamp]  /[skill]  [tool_count] tools  [completed]
...

FILES
───────────────────────────────────────────────────
Skills log:    ~/.claude/darwin/telemetry/skills.jsonl
Sessions log:  ~/.claude/darwin/telemetry/session_summaries.jsonl
Invocations:   ~/.claude/darwin/telemetry/invocations.jsonl

═══════════════════════════════════════════════════
```

---

## No Data Handling

If telemetry files are empty or missing, show:

```
═══════════════════════════════════════════════════
DARWIN - No Data Yet
═══════════════════════════════════════════════════

Telemetry hooks are configured but no data collected.

To start collecting data:
1. Start a NEW Claude session (hooks don't apply to current session)
2. Use some skills: /plan, /commit, /techdebt
3. Run /darwin status again

Hook Status:
- UserPromptSubmit: Configured ✓
- PostToolUse: Configured ✓
- Stop: Configured ✓

Config: ~/.claude/settings.json
═══════════════════════════════════════════════════
```

---

## Files Used

| File | Purpose |
|------|---------|
| `~/.claude/darwin/bin/evaluate.sh` | Fitness calculation |
| `~/.claude/darwin/telemetry/skills.jsonl` | Skill invocation log |
| `~/.claude/darwin/telemetry/session_summaries.jsonl` | Completion + tool counts |
| `~/.claude/darwin/config.yaml` | Tracked skills list |
