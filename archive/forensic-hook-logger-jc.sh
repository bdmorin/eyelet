#!/bin/bash
# forensic-hook-logger-jc.sh - PROPER JSONL Claude Code hook forensics with jc
# Each line is valid JSON, no embedded/escaped JSON strings
set -euo pipefail

HOOK_TYPE="${1:-unknown}"

# Clean timestamps (no invalid characters)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
DATE=$(date -u +"%Y-%m-%d") 
TIME_FILE=$(date -u +"%H:%M:%S_UTC")
EPOCH_TIME=$(date +%s)

# Configuration
LOG_DIR="${CLAUDE_HOOK_LOG_DIR:-./hooks-debug}"
DISABLE_LOGGING="${CLAUDE_HOOK_DISABLE:-0}"
MAX_FILE_SIZE="${CLAUDE_HOOK_MAX_SIZE:-10485760}"

[[ "$DISABLE_LOGGING" == "1" ]] && exit 0

# Check jc availability
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

# Safe JSON field extraction (returns proper JSON, not strings)
extract_json_field() {
    echo "$STDIN_DATA" | jq -r ".$1 // \"unknown\"" 2>/dev/null || echo "unknown"
}

extract_json_object() {
    echo "$STDIN_DATA" | jq ".$1 // {}" 2>/dev/null || echo "{}"
}

# Extract fields
TOOL_NAME=$(extract_json_field "tool_name")
SESSION_ID=$(extract_json_field "session_id")
CWD=$(extract_json_field "cwd")
TRANSCRIPT_PATH=$(extract_json_field "transcript_path")

# Handle hook-specific naming
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
PARENT_PID=$(ps -o ppid= -p $$ | tr -d ' ')

# jc-enhanced functions that return PROPER JSON (not JSON strings)
get_process_info() {
    local target_pid=$1
    
    if [[ $JC_AVAILABLE -eq 1 ]]; then
        ps -p $target_pid -o pid,ppid,pgid,user,comm,command,cpu,rss,vsz 2>/dev/null | jc --ps 2>/dev/null || echo "[]"
    else
        echo "[]"
    fi
}

get_environment() {
    if [[ $JC_AVAILABLE -eq 1 ]]; then
        env | jc --env 2>/dev/null || echo "{}"
    else
        echo "{}"
    fi
}

get_file_descriptors() {
    if [[ $JC_AVAILABLE -eq 1 ]] && command -v lsof >/dev/null; then
        lsof -p $$ 2>/dev/null | jc --lsof 2>/dev/null || echo "[]"
    else
        echo "[]"
    fi
}

get_process_network() {
    local target_pid=$1
    
    if [[ $JC_AVAILABLE -eq 1 ]] && command -v lsof >/dev/null; then
        lsof -p $target_pid -i 2>/dev/null | jc --lsof 2>/dev/null || echo "[]"
    else
        echo "[]"
    fi
}

get_system_info() {
    if [[ $JC_AVAILABLE -eq 1 ]]; then
        local uname_data=$(uname -a 2>/dev/null | jc --uname 2>/dev/null || echo "{}")
        local df_data=$(df -h . 2>/dev/null | jc --df 2>/dev/null || echo "[]")
        
        jq -n \
            --argjson uname "$uname_data" \
            --argjson df "$df_data" \
            --arg jc_available "true" \
            '{
                "uname": $uname,
                "disk_usage": $df,
                "jc_available": ($jc_available | test("true"))
            }'
    else
        echo '{"jc_available": false}'
    fi
}

# Create directory structure
SAFE_TOOL_NAME=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g')
TARGET_DIR="$LOG_DIR/$DATE/$HOOK_TYPE/$SAFE_TOOL_NAME"
mkdir -p "$TARGET_DIR"

# Filename
DESCRIPTION=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
# Ensure description is not empty
[[ -z "$DESCRIPTION" ]] && DESCRIPTION="unknown"
FILENAME="$DATE.$TIME_FILE.$DESCRIPTION.jc-forensic.jsonl"
FILEPATH="$TARGET_DIR/$FILENAME"

# Filter check
if [[ -n "${CLAUDE_HOOK_FILTER_TOOLS:-}" ]]; then
    if [[ ",$CLAUDE_HOOK_FILTER_TOOLS," != *",$TOOL_NAME,"* ]]; then
        exit 0
    fi
fi

# Truncate if needed
if [[ ${#STDIN_DATA} -gt $MAX_FILE_SIZE ]]; then
    STDIN_DATA="${STDIN_DATA:0:$MAX_FILE_SIZE}... [TRUNCATED]"
fi

# Create proper JSONL file (each line is valid JSON)
TEMP_FILE="$FILEPATH.tmp.$$"

{
    # Line 1: Metadata with proper JSON structure
    jq -n \
        --arg hook_type "$HOOK_TYPE" \
        --arg timestamp "$TIMESTAMP" \
        --arg session_id "$SESSION_ID" \
        --arg tool_name "$TOOL_NAME" \
        --arg cwd "$CWD" \
        --arg transcript_path "$TRANSCRIPT_PATH" \
        --arg log_file "$FILEPATH" \
        --arg hostname "$(hostname)" \
        --argjson pid "$PID" \
        --argjson ppid "$PARENT_PID" \
        --argjson epoch_time "$EPOCH_TIME" \
        --argjson jc_available "$JC_AVAILABLE" \
        --argjson data_size "${#STDIN_DATA}" \
        '{
            "type": "forensic_metadata",
            "hook_type": $hook_type,
            "timestamp": $timestamp,
            "session_id": $session_id,
            "tool_name": $tool_name,
            "cwd": $cwd,
            "transcript_path": $transcript_path,
            "log_file": $log_file,
            "hostname": $hostname,
            "pid": $pid,
            "ppid": $ppid,
            "epoch_time": $epoch_time,
            "jc_available": ($jc_available == 1),
            "data_size_bytes": $data_size
        }'

    # Line 2: Process information (proper JSON arrays/objects)
    jq -n \
        --argjson current_process "$(get_process_info $$)" \
        --argjson parent_process "$(get_process_info $PARENT_PID)" \
        --argjson file_descriptors "$(get_file_descriptors)" \
        --argjson network_connections "$(get_process_network $$)" \
        '{
            "type": "process_forensics",
            "current_process": $current_process,
            "parent_process": $parent_process,
            "file_descriptors": $file_descriptors,
            "network_connections": $network_connections
        }'

    # Line 3: Environment (proper JSON object)
    jq -n \
        --argjson environment "$(get_environment)" \
        '{
            "type": "environment",
            "data": $environment
        }'

    # Line 4: System context (proper JSON)
    jq -n \
        --argjson system "$(get_system_info)" \
        '{
            "type": "system_context",
            "data": $system
        }'

    # Line 5: Raw stdin (proper JSON string)
    jq -n \
        --arg raw_stdin "$STDIN_DATA" \
        '{
            "type": "raw_stdin",
            "data": $raw_stdin
        }'

    # Line 6: Tool input/output if available (proper JSON objects)
    tool_input=$(extract_json_object "tool_input")
    tool_response=$(extract_json_object "tool_response")
    
    jq -n \
        --argjson tool_input "$tool_input" \
        --argjson tool_response "$tool_response" \
        '{
            "type": "tool_context",
            "tool_input": $tool_input,
            "tool_response": $tool_response
        }'

} > "$TEMP_FILE"

# Atomic move
mv "$TEMP_FILE" "$FILEPATH"

# Optional index
if [[ "${CLAUDE_HOOK_CREATE_INDEX:-0}" == "1" ]]; then
    INDEX_FILE="$LOG_DIR/$DATE/jc-forensic-index.jsonl"
    jq -n \
        --arg timestamp "$TIMESTAMP" \
        --arg hook_type "$HOOK_TYPE" \
        --arg tool_name "$TOOL_NAME" \
        --arg session_id "$SESSION_ID" \
        --arg file "$FILEPATH" \
        --argjson jc_enhanced "$JC_AVAILABLE" \
        '{
            "timestamp": $timestamp,
            "hook_type": $hook_type,
            "tool_name": $tool_name,
            "session_id": $session_id,
            "file": $file,
            "jc_enhanced": ($jc_enhanced == 1)
        }' >> "$INDEX_FILE"
fi

# Cleanup
find "$TARGET_DIR" -name "*.tmp.*" -mmin +5 -delete 2>/dev/null || true

exit 0