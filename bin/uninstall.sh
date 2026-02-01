#!/bin/bash
# Darwin Skills Uninstaller

set -e

DARWIN_DIR="$HOME/.claude/darwin"
COMMANDS_DIR="$HOME/.claude/commands"
SETTINGS_FILE="$HOME/.claude/settings.json"
PLIST_FILE="$HOME/Library/LaunchAgents/com.darwin.weekly-evolution.plist"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "══════════════════════════════════════════════════════════"
echo "  DARWIN SKILLS UNINSTALLER"
echo "══════════════════════════════════════════════════════════"
echo ""

read -p "This will remove Darwin and all its data. Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Unload launchd job
if [ -f "$PLIST_FILE" ]; then
    echo "Removing scheduled job..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    rm -f "$PLIST_FILE"
fi

# Remove Darwin commands
echo "Removing skills..."
SKILLS=(darwin plan commit review-plan techdebt scaffold build-fix rams)
for skill in "${SKILLS[@]}"; do
    rm -f "$COMMANDS_DIR/$skill.md"
done

# Remove hooks from settings.json
if [ -f "$SETTINGS_FILE" ]; then
    echo "Removing hooks..."
    python3 << 'PYTHON_EOF'
import json
import sys

settings_file = "$HOME/.claude/settings.json".replace("$HOME", __import__("os").environ["HOME"])

try:
    with open(settings_file, "r") as f:
        settings = json.load(f)
except:
    sys.exit(0)

if "hooks" in settings:
    for hook_name in list(settings["hooks"].keys()):
        settings["hooks"][hook_name] = [
            h for h in settings["hooks"][hook_name]
            if "darwin" not in h.get("command", "")
        ]
        if not settings["hooks"][hook_name]:
            del settings["hooks"][hook_name]

    if not settings["hooks"]:
        del settings["hooks"]

with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2)
PYTHON_EOF
fi

# Remove Darwin directory
echo "Removing Darwin directory..."
rm -rf "$DARWIN_DIR"

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  UNINSTALL COMPLETE${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Darwin has been removed."
echo "Restart Claude Code to complete the uninstall."
echo ""
