# Darwin: Self-Evolving Skills for Claude Code

Darwin is an autonomous evolution system for Claude Code skills. It monitors how you use skills, measures their effectiveness, and automatically evolves underperforming ones.

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Telemetry  │────▶│  Evaluate   │────▶│   Evolve    │
│   (hooks)   │     │  (fitness)  │     │  (mutate)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
   skills.jsonl      weekly scores      new skill versions
```

1. **Telemetry** - Hooks capture every skill invocation and tool usage
2. **Evaluation** - Weekly fitness scores based on adoption, completion, efficiency
3. **Evolution** - Underperformers get module swaps; top performers stay stable

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/anirudhpareek/darwin-skills/main/install.sh | bash
```

Or clone and install manually:

```bash
git clone https://github.com/anirudhpareek/darwin-skills.git
cd darwin-skills
./install.sh
```

## What Gets Installed

```
~/.claude/
├── settings.json          # Hooks (merged with existing)
├── commands/
│   ├── darwin.md          # /darwin skill
│   ├── plan.md            # /plan skill
│   ├── commit.md          # /commit skill
│   └── ...                # Other skills
└── darwin/
    ├── bin/               # Scripts
    ├── modules/           # Module registry
    ├── skills/            # Skill definitions
    ├── telemetry/         # Usage data (generated)
    ├── evaluations/       # Weekly snapshots (generated)
    └── changelogs/        # Evolution history (generated)
```

## Included Skills

| Skill | Description |
|-------|-------------|
| `/darwin` | View system status, metrics, run evolution |
| `/plan` | Generate implementation plans |
| `/commit` | Smart conventional commits |
| `/review-plan` | Staff-engineer plan review |
| `/techdebt` | Find code smells and TODOs |
| `/scaffold` | Generate boilerplate matching patterns |
| `/build-fix` | Loop build until clean |
| `/rams` | Accessibility and design review |

## Usage

After installation, restart Claude Code and use skills normally:

```
/plan add user authentication
/commit
/darwin status
```

### Darwin Commands

```bash
# View skill fitness scores
/darwin status

# See evolution suggestions
/darwin suggest

# Manually trigger evolution
/darwin evolve
```

### Weekly Automation (macOS)

Darwin runs automatically every Sunday at 9 AM via launchd. Manage it with:

```bash
# Check status
launchctl list | grep darwin

# Disable
launchctl unload ~/Library/LaunchAgents/com.darwin.weekly-evolution.plist

# Enable
launchctl load ~/Library/LaunchAgents/com.darwin.weekly-evolution.plist
```

## How Skills Evolve

Skills are composed of **modules**:

| Module | Purpose |
|--------|---------|
| `input` | How arguments are handled |
| `research` | How context is gathered |
| `structure` | Output organization |
| `output` | Formatting style |
| `workflow` | Execution behavior |
| `validation` | Self-checking |

When a skill underperforms, Darwin swaps module versions:

```
/scaffold v1.0.0 (fitness: 0.17)
  └── input: v1 → v2 (mutation applied)
/scaffold v1.0.1 (fitness: TBD next week)
```

Changes are logged in `~/.claude/darwin/changelogs/`.

## Fitness Scoring

```
Fitness = 0.35 × Adoption + 0.30 × Completion + 0.25 × Efficiency + 0.10 × Trend
```

- **Adoption**: How often you use the skill vs others
- **Completion**: Sessions using this skill that end normally (not abandoned)
- **Efficiency**: Fewer tool calls = more efficient
- **Trend**: Is usage increasing or decreasing?

## Uninstall

```bash
~/.claude/darwin/bin/uninstall.sh
```

Or manually:
```bash
launchctl unload ~/Library/LaunchAgents/com.darwin.weekly-evolution.plist 2>/dev/null
rm -rf ~/.claude/darwin
rm ~/Library/LaunchAgents/com.darwin.weekly-evolution.plist
# Manually remove hooks from ~/.claude/settings.json
# Manually remove skills from ~/.claude/commands/
```

## Requirements

- macOS or Linux
- Python 3.6+
- PyYAML (`pip3 install pyyaml`)
- Claude Code CLI

## License

MIT License - do whatever you want with it.

## Contributing

PRs welcome! Ideas for improvement:
- Add more module variants
- Improve fitness metrics
- Cross-pollination between users' best modules
- Linux systemd timer support
