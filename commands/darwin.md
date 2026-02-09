---
description: Monitors, evaluates, and evolves Claude Code skills using fitness metrics. Analyzes skill performance, suggests mutations for underperformers, and tracks evolution history. Triggers on "skill status", "fitness scores", "evolve skills", "discover skills", "how are my skills doing", "check telemetry".
darwin_version: 1.3.0
darwin_modules:
  input: v2
  research: v3
  structure: v1
  output: v1
  workflow: v3
  validation: v3
disable-model-invocation: true
---

# Darwin - Skill Evolution System

Monitors, evaluates, and evolves Claude Code skills using fitness metrics.

## Quick Reference

| Command | Script | Purpose |
|---------|--------|---------|
| `status` | `evolve.py status` | Fitness dashboard (default) |
| `suggest` | `evolve.py suggest` | Preview mutations |
| `evolve` | `evolve.py cycle` | Full evolution cycle |
| `telemetry` | Read telemetry/*.json | View raw events |
| `discover` | `discover.py fetch` | Find trending skills |
| `install [name]` | `install-skill.sh` | Add external skill |

## Evolution Workflow

Copy this checklist to track progress:

```
Evolution Cycle:
- [ ] Step 1: Check status (python3 ~/.claude/darwin/bin/evolve.py status)
- [ ] Step 2: Review suggestions (python3 ~/.claude/darwin/bin/evolve.py suggest)
- [ ] Step 3: Apply mutations (python3 ~/.claude/darwin/bin/evolve.py apply)
- [ ] Step 4: Verify fitness improved (check changelog output)
- [ ] Step 5: If fitness dropped, consider rollback
```

## Command Details

### status (default)
```bash
python3 ~/.claude/darwin/bin/evolve.py status
```
Shows fitness scores for all tracked skills with classification:
- ★ Top performer (≥0.70)
- ✓ Healthy (≥0.50)
- ↓ Underperforming (≥0.35)
- ✗ Failing (<0.35)

### suggest
```bash
python3 ~/.claude/darwin/bin/evolve.py suggest
```
Shows recommended mutations without applying. Mutations include:
- **ABSORB**: Copy module from top performer
- **MUTATE**: Try alternative module variant

### evolve
```bash
python3 ~/.claude/darwin/bin/evolve.py cycle
```
Full cycle: evaluate → snapshot → apply mutations → verify fitness.

### discover
```bash
python3 ~/.claude/darwin/bin/discover.py fetch
```
Fetches trending skills from skills.sh with install counts.

### install
```bash
~/.claude/darwin/bin/install-skill.sh <skill-name>
```
Installs skill and adds to Darwin tracking.

## No Telemetry Data

If status shows no data:
1. Start a NEW Claude session (hooks activate on new sessions)
2. Use skills: `/plan`, `/commit`, `/techdebt`
3. Run `/darwin status` again

## Input

**Command:** $ARGUMENTS

If no arguments, defaults to `status`.

## Output Format

```
═══════════════════════════════════════════════════
DARWIN STATUS
═══════════════════════════════════════════════════

SKILL FITNESS
───────────────────────────────────────────────────
 1. /commit      ██████████ 0.91  ★
 2. /plan        ███████░░░ 0.72  ✓
═══════════════════════════════════════════════════
```

## Workflow

Execute immediately. Pause only if:
- Mutation would affect top performer
- No suggestions available (all variants tried)
