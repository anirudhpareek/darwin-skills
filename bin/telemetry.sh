#!/bin/bash
# Darwin Telemetry Logger
# Receives hook events from Claude Code and logs them for analysis
# Enhanced with session tracking and tool counting for fitness metrics

set -e

DARWIN_DIR="$HOME/.claude/darwin"
TELEMETRY_DIR="$DARWIN_DIR/telemetry"
SESSIONS_DIR="$TELEMETRY_DIR/sessions"
LOG_FILE="$TELEMETRY_DIR/invocations.jsonl"
SKILLS_LOG="$TELEMETRY_DIR/skills.jsonl"
SESSIONS_LOG="$TELEMETRY_DIR/session_summaries.jsonl"

# Ensure directories exist
mkdir -p "$TELEMETRY_DIR" "$SESSIONS_DIR"

# Read JSON from stdin
INPUT=$(cat)

# Parse event type from input
EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // "unknown"')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Session state file (tracks tool count and current skill)
SESSION_FILE="$SESSIONS_DIR/${SESSION_ID}.json"

# Helper: Get or create session state
get_session_state() {
  if [ -f "$SESSION_FILE" ]; then
    cat "$SESSION_FILE"
  else
    echo '{"tool_count": 0, "current_skill": null, "skill_start_time": null, "skills_used": []}'
  fi
}

# Helper: Update session state
update_session_state() {
  echo "$1" > "$SESSION_FILE"
}

case "$EVENT" in
  "UserPromptSubmit")
    # Check if this is a skill invocation (starts with /)
    PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""')
    if [[ "$PROMPT" =~ ^/([a-zA-Z0-9_-]+) ]]; then
      SKILL_NAME="${BASH_REMATCH[1]}"

      # Try to read module versions from skill file
      SKILL_FILE="$HOME/.claude/commands/${SKILL_NAME}.md"
      MODULES="{}"
      if [ -f "$SKILL_FILE" ]; then
        # Extract darwin_modules from frontmatter if present
        MODULES=$(awk '/^darwin_modules:/,/^---/' "$SKILL_FILE" 2>/dev/null | \
          grep -E '^\s+\w+:' | \
          sed 's/^[[:space:]]*//' | \
          awk -F': ' '{printf "\"%s\":\"%s\",", $1, $2}' | \
          sed 's/,$//' | \
          awk '{print "{"$0"}"}' 2>/dev/null || echo "{}")
        [ -z "$MODULES" ] && MODULES="{}"
      fi

      # Log skill invocation with modules
      jq -cn \
        --arg ts "$TIMESTAMP" \
        --arg session "$SESSION_ID" \
        --arg skill "$SKILL_NAME" \
        --arg prompt "$PROMPT" \
        --argjson modules "$MODULES" \
        '{timestamp: $ts, session_id: $session, event: "skill_start", skill: $skill, prompt: $prompt, modules: $modules}' >> "$SKILLS_LOG"

      # Update session state with current skill and modules
      STATE=$(get_session_state)
      NEW_STATE=$(echo "$STATE" | jq \
        --arg skill "$SKILL_NAME" \
        --arg ts "$TIMESTAMP" \
        --argjson modules "$MODULES" \
        '.current_skill = $skill | .skill_start_time = $ts | .tool_count = 0 | .skills_used += [$skill] | .current_modules = $modules')
      update_session_state "$NEW_STATE"
    fi
    ;;

  "PostToolUse")
    TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')

    # Log tool usage (without full input to save space)
    jq -cn \
      --arg ts "$TIMESTAMP" \
      --arg session "$SESSION_ID" \
      --arg tool "$TOOL_NAME" \
      '{timestamp: $ts, session_id: $session, event: "tool_use", tool: $tool}' >> "$LOG_FILE"

    # Increment tool count in session state
    STATE=$(get_session_state)
    NEW_STATE=$(echo "$STATE" | jq '.tool_count += 1')
    update_session_state "$NEW_STATE"
    ;;

  "Stop")
    # Response ended - write session summary if skill was active
    STATE=$(get_session_state)
    CURRENT_SKILL=$(echo "$STATE" | jq -r '.current_skill // "none"')
    TOOL_COUNT=$(echo "$STATE" | jq -r '.tool_count // 0')
    SKILL_START=$(echo "$STATE" | jq -r '.skill_start_time // null')
    MODULES=$(echo "$STATE" | jq -c '.current_modules // {}')

    if [ "$CURRENT_SKILL" != "none" ] && [ "$CURRENT_SKILL" != "null" ]; then
      # Write session summary for this skill invocation (with modules)
      jq -cn \
        --arg ts "$TIMESTAMP" \
        --arg session "$SESSION_ID" \
        --arg skill "$CURRENT_SKILL" \
        --arg start "$SKILL_START" \
        --argjson tools "$TOOL_COUNT" \
        --argjson modules "$MODULES" \
        '{timestamp: $ts, session_id: $session, event: "skill_complete", skill: $skill, start_time: $start, tool_count: $tools, modules: $modules, completed: true}' >> "$SESSIONS_LOG"

      # Reset current skill in session state
      NEW_STATE=$(echo "$STATE" | jq '.current_skill = null | .skill_start_time = null | .current_modules = {}')
      update_session_state "$NEW_STATE"
    fi

    # Also log response complete
    jq -cn \
      --arg ts "$TIMESTAMP" \
      --arg session "$SESSION_ID" \
      '{timestamp: $ts, session_id: $session, event: "response_complete"}' >> "$LOG_FILE"
    ;;

  "SessionStart")
    SOURCE=$(echo "$INPUT" | jq -r '.source // "unknown"')
    MODEL=$(echo "$INPUT" | jq -r '.model // "unknown"')

    # Initialize fresh session state
    jq -n \
      --arg model "$MODEL" \
      --arg source "$SOURCE" \
      --arg ts "$TIMESTAMP" \
      '{tool_count: 0, current_skill: null, skill_start_time: null, skills_used: [], model: $model, source: $source, started: $ts}' > "$SESSION_FILE"

    jq -cn \
      --arg ts "$TIMESTAMP" \
      --arg session "$SESSION_ID" \
      --arg source "$SOURCE" \
      --arg model "$MODEL" \
      '{timestamp: $ts, session_id: $session, event: "session_start", source: $source, model: $model}' >> "$LOG_FILE"
    ;;

  "SessionEnd")
    # Clean up session file
    rm -f "$SESSION_FILE" 2>/dev/null || true

    jq -cn \
      --arg ts "$TIMESTAMP" \
      --arg session "$SESSION_ID" \
      '{timestamp: $ts, session_id: $session, event: "session_end"}' >> "$LOG_FILE"
    ;;
esac

# Always exit 0 to not block Claude
exit 0
