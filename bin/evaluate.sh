#!/bin/bash
# Darwin Fitness Evaluator
# Calculates fitness scores for skills based on telemetry data

set -e

DARWIN_DIR="$HOME/.claude/darwin"
TELEMETRY_DIR="$DARWIN_DIR/telemetry"
EVALUATIONS_DIR="$DARWIN_DIR/evaluations"
SKILLS_LOG="$TELEMETRY_DIR/skills.jsonl"
SESSIONS_LOG="$TELEMETRY_DIR/session_summaries.jsonl"

# Ensure directories exist
mkdir -p "$EVALUATIONS_DIR"

# Get current week for snapshots
CURRENT_WEEK=$(date -u +"%Y-W%V")

# Date range (last 7 days)
if [[ "$OSTYPE" == "darwin"* ]]; then
    WEEK_AGO=$(date -v-7d -u +"%Y-%m-%dT00:00:00Z")
    TWO_WEEKS_AGO=$(date -v-14d -u +"%Y-%m-%dT00:00:00Z")
else
    WEEK_AGO=$(date -d "7 days ago" -u +"%Y-%m-%dT00:00:00Z")
    TWO_WEEKS_AGO=$(date -d "14 days ago" -u +"%Y-%m-%dT00:00:00Z")
fi

# Check if we have data
if [ ! -f "$SKILLS_LOG" ] || [ ! -s "$SKILLS_LOG" ]; then
    echo '{"error": "No telemetry data found", "skills": []}'
    exit 0
fi

# Get all tracked skills from config
TRACKED_SKILLS=$(cat "$DARWIN_DIR/config.yaml" 2>/dev/null | grep -A20 "tracked_skills:" | grep "^  - " | sed 's/^  - //' | tr '\n' ' ')
if [ -z "$TRACKED_SKILLS" ]; then
    TRACKED_SKILLS="plan review-plan techdebt commit scaffold build-fix rams darwin"
fi

# Count total skill invocations this week
TOTAL_THIS_WEEK=$(cat "$SKILLS_LOG" 2>/dev/null | jq -s --arg since "$WEEK_AGO" '[.[] | select(.timestamp >= $since)] | length')
TOTAL_LAST_WEEK=$(cat "$SKILLS_LOG" 2>/dev/null | jq -s --arg since "$TWO_WEEKS_AGO" --arg until "$WEEK_AGO" '[.[] | select(.timestamp >= $since and .timestamp < $until)] | length')

# Initialize results array
RESULTS="[]"

for SKILL in $TRACKED_SKILLS; do
    # Count invocations this week
    INVOCATIONS_THIS_WEEK=$(cat "$SKILLS_LOG" 2>/dev/null | jq -s --arg skill "$SKILL" --arg since "$WEEK_AGO" '[.[] | select(.skill == $skill and .timestamp >= $since)] | length')

    # Count invocations last week (for trend)
    INVOCATIONS_LAST_WEEK=$(cat "$SKILLS_LOG" 2>/dev/null | jq -s --arg skill "$SKILL" --arg since "$TWO_WEEKS_AGO" --arg until "$WEEK_AGO" '[.[] | select(.skill == $skill and .timestamp >= $since and .timestamp < $until)] | length')

    # Get completion data if session summaries exist
    if [ -f "$SESSIONS_LOG" ] && [ -s "$SESSIONS_LOG" ]; then
        COMPLETIONS=$(cat "$SESSIONS_LOG" | jq -s --arg skill "$SKILL" --arg since "$WEEK_AGO" '[.[] | select(.skill == $skill and .timestamp >= $since and .completed == true)] | length')
        TOTAL_SESSIONS=$(cat "$SESSIONS_LOG" | jq -s --arg skill "$SKILL" --arg since "$WEEK_AGO" '[.[] | select(.skill == $skill and .timestamp >= $since)] | length')
        AVG_TOOLS=$(cat "$SESSIONS_LOG" | jq -s --arg skill "$SKILL" --arg since "$WEEK_AGO" '[.[] | select(.skill == $skill and .timestamp >= $since) | .tool_count] | if length > 0 then add / length else 0 end')
    else
        COMPLETIONS=0
        TOTAL_SESSIONS=0
        AVG_TOOLS=0
    fi

    # Calculate metrics (0-1 scale)

    # 1. Adoption: What % of total invocations is this skill?
    if [ "$TOTAL_THIS_WEEK" -gt 0 ]; then
        ADOPTION=$(echo "scale=2; $INVOCATIONS_THIS_WEEK / $TOTAL_THIS_WEEK" | bc)
    else
        ADOPTION="0"
    fi

    # 2. Completion Rate: What % of invocations completed?
    if [ "$TOTAL_SESSIONS" -gt 0 ]; then
        COMPLETION_RATE=$(echo "scale=2; $COMPLETIONS / $TOTAL_SESSIONS" | bc)
    elif [ "$INVOCATIONS_THIS_WEEK" -gt 0 ]; then
        # If no session data, assume 80% completion (generous default)
        COMPLETION_RATE="0.80"
    else
        COMPLETION_RATE="0"
    fi

    # 3. Efficiency: Inverse of tool count (fewer tools = more efficient)
    # Normalize: 1 tool = 1.0, 10 tools = 0.1, cap at 0.1 minimum
    if [ "$(echo "$AVG_TOOLS > 0" | bc)" -eq 1 ]; then
        EFFICIENCY=$(echo "scale=2; if (1 / $AVG_TOOLS > 1) 1 else if (1 / $AVG_TOOLS < 0.1) 0.1 else 1 / $AVG_TOOLS fi fi" | bc 2>/dev/null || echo "0.50")
    else
        EFFICIENCY="0.50"  # Default if no data
    fi

    # 4. Trend: This week vs last week (1.0 = same, >1 = growing, <1 = declining)
    if [ "$INVOCATIONS_LAST_WEEK" -gt 0 ]; then
        TREND=$(echo "scale=2; $INVOCATIONS_THIS_WEEK / $INVOCATIONS_LAST_WEEK" | bc)
    elif [ "$INVOCATIONS_THIS_WEEK" -gt 0 ]; then
        TREND="2.0"  # New skill with usage = growing
    else
        TREND="0"    # No usage
    fi
    # Normalize trend to 0-1 scale (0.5 = declining, 1.0 = doubling+)
    TREND_NORM=$(echo "scale=2; if ($TREND > 2) 1 else $TREND / 2 fi" | bc 2>/dev/null || echo "0.50")

    # Composite Fitness Score
    # fitness = 0.35×adoption + 0.30×completion + 0.25×efficiency + 0.10×trend
    FITNESS=$(echo "scale=2; 0.35 * $ADOPTION + 0.30 * $COMPLETION_RATE + 0.25 * $EFFICIENCY + 0.10 * $TREND_NORM" | bc 2>/dev/null || echo "0")

    # Build skill result JSON
    SKILL_RESULT=$(jq -n \
        --arg skill "$SKILL" \
        --argjson invocations "$INVOCATIONS_THIS_WEEK" \
        --argjson adoption "$ADOPTION" \
        --argjson completion "$COMPLETION_RATE" \
        --argjson efficiency "$EFFICIENCY" \
        --argjson trend "$TREND_NORM" \
        --argjson fitness "$FITNESS" \
        --argjson avg_tools "${AVG_TOOLS:-0}" \
        '{
            skill: $skill,
            invocations: $invocations,
            metrics: {
                adoption: $adoption,
                completion: $completion,
                efficiency: $efficiency,
                trend: $trend
            },
            fitness: $fitness,
            avg_tools: $avg_tools
        }')

    # Append to results
    RESULTS=$(echo "$RESULTS" | jq --argjson item "$SKILL_RESULT" '. += [$item]')
done

# Sort by fitness descending
SORTED_RESULTS=$(echo "$RESULTS" | jq 'sort_by(-.fitness)')

# Build final output
jq -n \
    --arg week "$CURRENT_WEEK" \
    --arg since "$WEEK_AGO" \
    --argjson total "$TOTAL_THIS_WEEK" \
    --argjson skills "$SORTED_RESULTS" \
    '{
        week: $week,
        period_start: $since,
        total_invocations: $total,
        skills: $skills
    }'
