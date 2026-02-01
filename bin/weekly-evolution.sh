#!/bin/bash
# Darwin Weekly Evolution
# Runs the full evolution cycle and logs output
# Scheduled via launchd to run every Sunday at 9:00 AM

set -e

DARWIN_DIR="$HOME/.claude/darwin"
LOG_DIR="$DARWIN_DIR/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/evolution_${TIMESTAMP}.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Start logging
exec > >(tee -a "$LOG_FILE") 2>&1

echo "════════════════════════════════════════════════════════════"
echo "DARWIN WEEKLY EVOLUTION"
echo "Started: $(date)"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if we have enough data to evolve
SKILLS_LOG="$DARWIN_DIR/telemetry/skills.jsonl"
if [ ! -f "$SKILLS_LOG" ] || [ ! -s "$SKILLS_LOG" ]; then
    echo "No telemetry data found. Skipping evolution."
    echo "Use some skills first, then evolution will have data to work with."
    exit 0
fi

# Count invocations this week
INVOCATIONS=$(wc -l < "$SKILLS_LOG" | tr -d ' ')
echo "Total skill invocations recorded: $INVOCATIONS"
echo ""

# Minimum threshold to run evolution
MIN_INVOCATIONS=3
if [ "$INVOCATIONS" -lt "$MIN_INVOCATIONS" ]; then
    echo "Not enough data to evolve (need at least $MIN_INVOCATIONS invocations)."
    echo "Keep using skills and evolution will run next week."
    exit 0
fi

# Run evolution cycle
echo "Running evolution cycle..."
echo ""
python3 "$DARWIN_DIR/bin/evolve.py" cycle

echo ""
echo "════════════════════════════════════════════════════════════"
echo "EVOLUTION COMPLETE"
echo "Finished: $(date)"
echo "Log saved: $LOG_FILE"
echo "════════════════════════════════════════════════════════════"

# Clean up old logs (keep last 12 weeks)
find "$LOG_DIR" -name "evolution_*.log" -mtime +90 -delete 2>/dev/null || true

# Send notification (macOS)
if command -v osascript &> /dev/null; then
    osascript -e 'display notification "Evolution cycle complete. Check changelogs for updates." with title "Darwin"' 2>/dev/null || true
fi
