#!/bin/bash
# forensic-fixed.sh - WORKING JSONL forensic logger with proper JSON validation
set -euo pipefail

HOOK_TYPE="${1:-unknown}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DATE=$(date -u +"%Y-%m-%d") 
TIME_FILE=$(date -u +"%H:%M:%S_UTC")

LOG_DIR="${CLAUDE_HOOK_LOG_DIR:-./hooks-debug}"
[[ "${CLAUDE_HOOK_DISABLE:-0}" == "1" ]] && exit 0

# Check if jc is available
JC_AVAILABLE=0
if command -v jc >/dev/null 2>&1; then
    JC_AVAILABLE=1
fi

# Read stdin
STDIN_DATA=""
while IFS= read -r line; do
    STDIN_DATA+="$line"$'\n'
done
STDIN_DATA="${STDIN_DATA%$'\n'}"

# Safe field extraction - always returns valid values
get_field() {
    local field="$1"
    local result
    result=$(echo "$STDIN_DATA" | jq -r ".$field // \"unknown\"" 2>/dev/null || echo "unknown")
    # Ensure result is safe for JSON
    echo "$result" | sed 's/"/\\"/g'
}

# Safe JSON object extraction - always returns valid JSON
get_json_object() {
    local field="$1"
    local result
    result=$(echo "$STDIN_DATA" | jq ".$field // {}" 2>/dev/null)
    # Validate it's actually valid JSON
    if echo "$result" | jq . >/dev/null 2>&1; then
        echo "$result"
    else
        echo "{}"
    fi
}

# Extract basic fields safely
TOOL_NAME=$(get_field "tool_name")
SESSION_ID=$(get_field "session_id")
CWD=$(get_field "cwd")
TRANSCRIPT_PATH=$(get_field "transcript_path")

# Handle unknown tool names
if [[ "$TOOL_NAME" == "unknown" ]]; then
    case "$HOOK_TYPE" in
        "UserPromptSubmit") TOOL_NAME="UserPrompt" ;;
        "Notification") TOOL_NAME="SystemNotification" ;;
        "Stop") TOOL_NAME="SessionStop" ;;
        "SubagentStop") TOOL_NAME="SubagentStop" ;;
        "PreCompact") TOOL_NAME="ContextCompact" ;;
        *) TOOL_NAME="UnknownTool" ;;
    esac
fi

# Process info
PID=$$
PARENT_PID=$(ps -o ppid= -p $$ | tr -d ' ' || echo "0")

# jc-enhanced data collection
get_process_data() {
    if [[ $JC_AVAILABLE -eq 1 ]]; then
        ps -p $$ -o pid,ppid,pgid,user,comm,command 2>/dev/null | jc --ps 2>/dev/null || echo "[]"
    else
        echo "[]"
    fi
}

get_environment_data() {
    if [[ $JC_AVAILABLE -eq 1 ]]; then
        env | jc --env 2>/dev/null || echo "{}"
    else
        # Fallback - create safe JSON manually
        echo '{"USER":"'${USER:-unknown}'","SHELL":"'${SHELL:-unknown}'","PWD":"'${PWD:-unknown}'"}'
    fi
}

get_network_data() {
    if [[ $JC_AVAILABLE -eq 1 ]] && command -v lsof >/dev/null; then
        lsof -p $$ -i 2>/dev/null | jc --lsof 2>/dev/null || echo "[]"
    else
        echo "[]"
    fi
}

get_file_descriptors() {
    if [[ $JC_AVAILABLE -eq 1 ]] && command -v lsof >/dev/null; then
        lsof -p $$ 2>/dev/null | jc --lsof 2>/dev/null | jq 'map(select(.type == "REG" or .type == "PIPE" or .type == "CHR"))' 2>/dev/null || echo "[]"
    else
        local fd_count=0
        if [[ -d "/proc/$$/fd" ]]; then
            fd_count=$(ls /proc/$$/fd 2>/dev/null | wc -l || echo 0)
        fi
        echo "[{\"fd_count\": $fd_count}]"
    fi
}

# Setup paths
SAFE_TOOL_NAME=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g')
TARGET_DIR="$LOG_DIR/$DATE/$HOOK_TYPE/$SAFE_TOOL_NAME"
mkdir -p "$TARGET_DIR"

DESCRIPTION=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
[[ -z "$DESCRIPTION" ]] && DESCRIPTION="unknown"

if [[ $JC_AVAILABLE -eq 1 ]]; then
    FILENAME="$DATE.$TIME_FILE.$DESCRIPTION.jc-forensic.jsonl"
else
    FILENAME="$DATE.$TIME_FILE.$DESCRIPTION.basic-forensic.jsonl"
fi
FILEPATH="$TARGET_DIR/$FILENAME"

# Create JSONL file - each line is valid JSON
TEMP_FILE="$FILEPATH.tmp.$$"

{
    # Line 1: Metadata
    jq -nc \
        --arg type "forensic_metadata" \
        --arg hook_type "$HOOK_TYPE" \
        --arg timestamp "$TIMESTAMP" \
        --arg tool_name "$TOOL_NAME" \
        --arg session_id "$SESSION_ID" \
        --arg cwd "$CWD" \
        --arg transcript_path "$TRANSCRIPT_PATH" \
        --argjson pid "$PID" \
        --argjson ppid "$PARENT_PID" \
        --argjson jc_available "$JC_AVAILABLE" \
        '{
            type: $type,
            hook_type: $hook_type,
            timestamp: $timestamp,
            tool_name: $tool_name,
            session_id: $session_id,
            cwd: $cwd,
            transcript_path: $transcript_path,
            pid: $pid,
            ppid: $ppid,
            jc_available: ($jc_available == 1)
        }'

    # Line 2: Process information
    PROCESS_DATA=$(get_process_data)
    echo "$PROCESS_DATA" | jq -c '{type: "process_info", data: .}'

    # Line 3: Environment
    ENV_DATA=$(get_environment_data)
    echo "$ENV_DATA" | jq -c '{type: "environment", data: .}'

    # Line 4: File descriptors
    FD_DATA=$(get_file_descriptors)
    echo "$FD_DATA" | jq -c '{type: "file_descriptors", data: .}'

    # Line 5: Network connections (process-specific)
    NET_DATA=$(get_network_data)
    echo "$NET_DATA" | jq -c '{type: "network_connections", data: .}'

    # Line 6: Tool context (safe handling)
    TOOL_INPUT=$(get_json_object "tool_input")
    TOOL_RESPONSE=$(get_json_object "tool_response")
    
    # Always use string args to avoid --argjson issues
    jq -nc \
        --arg tool_input_str "$TOOL_INPUT" \
        --arg tool_response_str "$TOOL_RESPONSE" \
        '{
            type: "tool_context",
            tool_input_raw: $tool_input_str,
            tool_response_raw: $tool_response_str
        }'

    # Line 7: Raw stdin (last line)
    jq -nc --arg data "$STDIN_DATA" '{type: "raw_stdin", data: $data}'

} > "$TEMP_FILE"

# Atomic move
mv "$TEMP_FILE" "$FILEPATH"

# Cleanup old temp files
find "$TARGET_DIR" -name "*.tmp.*" -mmin +5 -delete 2>/dev/null || true

exit 0