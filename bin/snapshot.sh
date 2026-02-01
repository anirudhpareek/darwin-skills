#!/bin/bash
# Darwin Weekly Snapshot
# Saves current fitness evaluation to evaluations directory for trend analysis

set -e

DARWIN_DIR="$HOME/.claude/darwin"
EVALUATIONS_DIR="$DARWIN_DIR/evaluations"

# Ensure directory exists
mkdir -p "$EVALUATIONS_DIR"

# Get current week
CURRENT_WEEK=$(date -u +"%Y-W%V")
SNAPSHOT_FILE="$EVALUATIONS_DIR/${CURRENT_WEEK}.json"

# Run evaluation and save
EVALUATION=$("$DARWIN_DIR/bin/evaluate.sh")

# Add snapshot metadata
SNAPSHOT=$(echo "$EVALUATION" | jq \
    --arg snapshot_time "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    '. + {snapshot_time: $snapshot_time}')

# Save snapshot
echo "$SNAPSHOT" > "$SNAPSHOT_FILE"

echo "Snapshot saved: $SNAPSHOT_FILE"

# Clean up old snapshots (keep last 12 weeks)
find "$EVALUATIONS_DIR" -name "*.json" -mtime +90 -delete 2>/dev/null || true

# Output the snapshot
cat "$SNAPSHOT_FILE"
