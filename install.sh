#!/bin/bash
# Darwin Skills Installer
# Installs the self-evolving skills system for Claude Code

set -e

DARWIN_DIR="$HOME/.claude/darwin"
COMMANDS_DIR="$HOME/.claude/commands"
SETTINGS_FILE="$HOME/.claude/settings.json"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "══════════════════════════════════════════════════════════"
echo "  DARWIN SKILLS INSTALLER"
echo "══════════════════════════════════════════════════════════"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check for PyYAML
if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${YELLOW}Installing PyYAML...${NC}"
    pip3 install pyyaml --quiet
fi

# Determine script directory (works for both git clone and curl | bash)
if [ -d "$(dirname "$0")/bin" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
else
    # Running from curl | bash, need to download
    echo "Downloading Darwin..."
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    curl -fsSL https://github.com/anirudhpareek/darwin-skills/archive/main.tar.gz | tar xz
    SCRIPT_DIR="$TEMP_DIR/darwin-skills-main"
fi

echo "Installing from: $SCRIPT_DIR"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p "$DARWIN_DIR"/{bin,modules,skills,telemetry,evaluations,changelogs,logs}
mkdir -p "$COMMANDS_DIR"
mkdir -p "$LAUNCH_AGENTS"

# Copy bin scripts
echo "Installing scripts..."
cp "$SCRIPT_DIR/bin/"* "$DARWIN_DIR/bin/"
chmod +x "$DARWIN_DIR/bin/"*.sh
chmod +x "$DARWIN_DIR/bin/"*.py

# Copy modules
echo "Installing modules..."
cp "$SCRIPT_DIR/modules/"* "$DARWIN_DIR/modules/"

# Copy skill definitions
echo "Installing skill definitions..."
cp "$SCRIPT_DIR/skills/"* "$DARWIN_DIR/skills/"

# Copy command files
echo "Installing commands..."
cp "$SCRIPT_DIR/commands/"* "$COMMANDS_DIR/"

# Merge hooks into settings.json
echo "Configuring hooks..."

HOOKS_JSON=$(cat <<'HOOKS_EOF'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "$HOME/.claude/darwin/bin/telemetry.sh user_prompt \"$CLAUDE_PROMPT\"",
        "async": true,
        "timeout": 5
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "$HOME/.claude/darwin/bin/telemetry.sh tool_use \"$CLAUDE_TOOL_NAME\"",
        "async": true,
        "timeout": 5
      }
    ],
    "SessionStart": [
      {
        "type": "command",
        "command": "$HOME/.claude/darwin/bin/telemetry.sh session_start",
        "async": true,
        "timeout": 5
      }
    ],
    "SessionEnd": [
      {
        "type": "command",
        "command": "$HOME/.claude/darwin/bin/telemetry.sh session_end",
        "async": true,
        "timeout": 5
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "$HOME/.claude/darwin/bin/telemetry.sh stop",
        "async": true,
        "timeout": 5
      }
    ]
  }
}
HOOKS_EOF
)

HOOKS_TMP=$(mktemp)
echo "$HOOKS_JSON" > "$HOOKS_TMP"

if [ -f "$SETTINGS_FILE" ]; then
    # Merge with existing settings
    python3 - "$SETTINGS_FILE" "$HOOKS_TMP" << 'PYTHON_EOF'
import json, sys

settings_file = sys.argv[1]
hooks_file = sys.argv[2]

with open(settings_file, "r") as f:
    settings = json.load(f)

with open(hooks_file, "r") as f:
    new_hooks = json.load(f)

if "hooks" not in settings:
    settings["hooks"] = {}

for hook_name, hook_list in new_hooks["hooks"].items():
    if hook_name not in settings["hooks"]:
        settings["hooks"][hook_name] = []
    # Check if darwin hook already exists
    existing_commands = [h.get("command", "") for h in settings["hooks"][hook_name]]
    for hook in hook_list:
        if hook["command"] not in existing_commands:
            settings["hooks"][hook_name].append(hook)

with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2)

print("  Merged hooks into existing settings.json")
PYTHON_EOF
else
    echo "$HOOKS_JSON" > "$SETTINGS_FILE"
    echo "  Created new settings.json"
fi

rm -f "$HOOKS_TMP"

# Compile skills
echo "Compiling skills..."
python3 "$DARWIN_DIR/bin/compile.py" all

# Set up launchd (macOS only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Setting up weekly automation..."

    PLIST_FILE="$LAUNCH_AGENTS/com.darwin.weekly-evolution.plist"

    cat > "$PLIST_FILE" << PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.darwin.weekly-evolution</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$HOME/.claude/darwin/bin/weekly-evolution.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$HOME/.claude/darwin/logs/launchd_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.claude/darwin/logs/launchd_stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>$HOME</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PLIST_EOF

    # Unload if already loaded, then reload
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    launchctl load "$PLIST_FILE"
    echo "  Weekly evolution scheduled for Sundays at 9 AM"
else
    echo -e "${YELLOW}Note: Automatic weekly evolution is macOS-only.${NC}"
    echo "  On Linux, add a cron job:"
    echo "  0 9 * * 0 $DARWIN_DIR/bin/weekly-evolution.sh"
fi

# Clean up temp directory if we created one
if [ -n "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  INSTALLATION COMPLETE${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Installed skills:"
echo "  /darwin    - View status and trigger evolution"
echo "  /plan      - Generate implementation plans"
echo "  /commit    - Smart conventional commits"
echo "  /techdebt  - Find code smells and TODOs"
echo "  /scaffold  - Generate matching boilerplate"
echo "  /build-fix - Loop build until clean"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to activate hooks"
echo "  2. Use skills normally - telemetry will track usage"
echo "  3. Run '/darwin status' to see metrics"
echo ""
