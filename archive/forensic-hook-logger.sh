#!/bin/bash
# forensic-hook-logger.sh - COMPLETE Claude Code hook forensic analysis
# Captures EVERYTHING: known context + unknown via /proc introspection
set -euo pipefail

# Hook type passed as first argument
HOOK_TYPE="${1:-unknown}"

# Forensic timestamps
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%6NZ")
DATE=$(date -u +"%Y-%m-%d") 
TIME_FILE=$(date -u +"%H:%M:%S_UTC")
EPOCH_TIME=$(date +%s.%6N)

# Configuration
LOG_DIR="${CLAUDE_HOOK_LOG_DIR:-./hooks-debug}"
DISABLE_LOGGING="${CLAUDE_HOOK_DISABLE:-0}"
MAX_FILE_SIZE="${CLAUDE_HOOK_MAX_SIZE:-10485760}"  # 10MB for forensics
ENABLE_PROC_DEBUG="${CLAUDE_HOOK_PROC_DEBUG:-1}"

# Exit early if logging disabled
[[ "$DISABLE_LOGGING" == "1" ]] && exit 0

# Read all stdin data
STDIN_DATA=""
while IFS= read -r line; do
    STDIN_DATA+="$line"$'\n'
done
STDIN_DATA="${STDIN_DATA%$'\n'}"

# Enhanced JSON extraction
extract_json_field() {
    echo "$STDIN_DATA" | jq -r ".$1 // \"unknown\"" 2>/dev/null || echo "unknown"
}

extract_json_object() {
    echo "$STDIN_DATA" | jq ".$1 // {}" 2>/dev/null || echo "{}"
}

# Extract ALL known fields
TOOL_NAME=$(extract_json_field "tool_name")
SESSION_ID=$(extract_json_field "session_id")
CWD=$(extract_json_field "cwd")
TRANSCRIPT_PATH=$(extract_json_field "transcript_path")
PROMPT=$(extract_json_field "prompt")
MESSAGE=$(extract_json_field "message")
REASON=$(extract_json_field "reason")
TOOL_INPUT=$(extract_json_object "tool_input")
TOOL_RESPONSE=$(extract_json_object "tool_response")

# Handle hook-specific tool naming
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

# Forensic process information
PID=$$
PARENT_PID=$(ps -o ppid= -p $$ | tr -d ' ')
PGID=$(ps -o pgid= -p $$ | tr -d ' ')

# /proc filesystem forensics (Linux/macOS compatible)
capture_proc_info() {
    local target_pid=$1
    local proc_data="{}"
    
    if [[ -d "/proc/$target_pid" ]]; then
        # Linux /proc system
        proc_data=$(cat << EOF
{
  "cmdline": $(cat /proc/$target_pid/cmdline 2>/dev/null | tr '\0' ' ' | jq -R -s '.' || echo '""'),
  "environ": $(cat /proc/$target_pid/environ 2>/dev/null | tr '\0' '\n' | jq -R -s '.' || echo '""'),
  "cwd": $(readlink /proc/$target_pid/cwd 2>/dev/null | jq -R '.' || echo '""'),
  "exe": $(readlink /proc/$target_pid/exe 2>/dev/null | jq -R '.' || echo '""'),
  "fd_count": $(ls /proc/$target_pid/fd 2>/dev/null | wc -l || echo 0),
  "status": $(cat /proc/$target_pid/status 2>/dev/null | jq -R -s '.' || echo '""'),
  "limits": $(cat /proc/$target_pid/limits 2>/dev/null | jq -R -s '.' || echo '""'),
  "maps": $(head -20 /proc/$target_pid/maps 2>/dev/null | jq -R -s '.' || echo '""')
}
EOF
        )
    else
        # macOS fallback using ps and lsof
        local cmd_info=$(ps -p $target_pid -o pid,ppid,pgid,command 2>/dev/null || echo "")
        local fd_info=$(lsof -p $target_pid 2>/dev/null | head -20 || echo "")
        
        proc_data=$(cat << EOF
{
  "ps_info": $(echo "$cmd_info" | jq -R -s '.'),
  "open_files": $(echo "$fd_info" | jq -R -s '.'),
  "platform": "darwin"
}
EOF
        )
    fi
    
    echo "$proc_data"
}

# Complete environment capture
capture_environment() {
    echo "{"
    env | while IFS='=' read -r key value; do
        printf '  "%s": %s,\n' "$key" "$(printf '%s' "$value" | jq -R '.')"
    done | sed '$ s/,$//'
    echo "}"
}

# File descriptor analysis
capture_fd_info() {
    if command -v lsof >/dev/null; then
        lsof -p $$ 2>/dev/null | jq -R -s '.' || echo '""'
    else
        echo '""'
    fi
}

# Network connections
capture_network_info() {
    if command -v netstat >/dev/null; then
        netstat -an 2>/dev/null | head -20 | jq -R -s '.' || echo '""'
    else
        echo '""'
    fi
}

# System context
capture_system_context() {
    cat << EOF
{
  "uname": $(uname -a 2>/dev/null | jq -R '.' || echo '""'),
  "uptime": $(uptime 2>/dev/null | jq -R '.' || echo '""'),
  "load_avg": $(cat /proc/loadavg 2>/dev/null | jq -R '.' || echo '""'),
  "memory": $(free -h 2>/dev/null | jq -R -s '.' || echo '""'),
  "disk_usage": $(df -h . 2>/dev/null | jq -R -s '.' || echo '""'),
  "process_tree": $(pstree -p $$ 2>/dev/null | jq -R '.' || echo '""')
}
EOF
}

# Unknown data discovery - extract ALL JSON keys
discover_unknown_fields() {
    # Get all keys and filter out known ones
    local known_keys="session_id tool_name cwd transcript_path prompt message reason tool_input tool_response hook_event_name"
    echo "$STDIN_DATA" | jq --argjson known '["session_id","tool_name","cwd","transcript_path","prompt","message","reason","tool_input","tool_response","hook_event_name"]' 'with_entries(select(.key as $k | $known | index($k) | not))' 2>/dev/null || echo "{}"
}

# Directory structure
SAFE_TOOL_NAME=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g')
TARGET_DIR="$LOG_DIR/$DATE/$HOOK_TYPE/$SAFE_TOOL_NAME"
mkdir -p "$TARGET_DIR"

# Forensic filename
DESCRIPTION=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
FILENAME="$DATE.$TIME_FILE.$DESCRIPTION.forensic.jsonl"
FILEPATH="$TARGET_DIR/$FILENAME"

# Filter check
if [[ -n "${CLAUDE_HOOK_FILTER_TOOLS:-}" ]]; then
    if [[ ",$CLAUDE_HOOK_FILTER_TOOLS," != *",$TOOL_NAME,"* ]]; then
        exit 0
    fi
fi

# Truncate if too large
if [[ ${#STDIN_DATA} -gt $MAX_FILE_SIZE ]]; then
    STDIN_DATA="${STDIN_DATA:0:$MAX_FILE_SIZE}... [TRUNCATED]"
fi

# Create comprehensive forensic log
TEMP_FILE="$FILEPATH.tmp.$$"

{
    # Line 1: Complete forensic metadata
    cat << EOF
{
  "forensic_meta": {
    "version": "1.0",
    "hook_type": "$HOOK_TYPE",
    "timestamp": "$TIMESTAMP",
    "epoch_time": $EPOCH_TIME,
    "log_file": "$FILEPATH",
    "session_id": "$SESSION_ID",
    "tool_name": "$TOOL_NAME",
    "forensic_pid": $$,
    "hostname": "$(hostname)"
  },
  "claude_context": {
    "session_id": "$SESSION_ID",
    "tool_name": "$TOOL_NAME",
    "cwd": "$CWD",
    "transcript_path": "$TRANSCRIPT_PATH",
    "hook_event_name": "$HOOK_TYPE",
    "prompt": "$PROMPT",
    "message": "$MESSAGE",
    "reason": "$REASON",
    "tool_input": $TOOL_INPUT,
    "tool_response": $TOOL_RESPONSE
  },
  "process_forensics": {
    "pid": $$,
    "ppid": $PARENT_PID,
    "pgid": $PGID,
    "proc_info": $(capture_proc_info $$),
    "parent_proc": $(capture_proc_info $PARENT_PID),
    "file_descriptors": $(capture_fd_info),
    "network_connections": $(capture_network_info)
  },
  "environment_complete": $(capture_environment),
  "system_context": $(capture_system_context),
  "unknown_fields": $(discover_unknown_fields),
  "performance": {
    "log_timestamp": "$TIMESTAMP",
    "data_size_bytes": ${#STDIN_DATA},
    "proc_debug_enabled": $ENABLE_PROC_DEBUG
  }
}
EOF
    
    # Line 2: Raw stdin (unchanged)
    echo "$STDIN_DATA"
    
    # Line 3: Transcript content (if accessible)
    if [[ -f "$TRANSCRIPT_PATH" && "$TRANSCRIPT_PATH" != "unknown" ]]; then
        echo '{"type":"transcript_snapshot","timestamp":"'$TIMESTAMP'","content":'$(tail -5 "$TRANSCRIPT_PATH" | jq -R -s '.')'}' 
    fi
    
} > "$TEMP_FILE"

# Atomic move
mv "$TEMP_FILE" "$FILEPATH"

# Optional index
if [[ "${CLAUDE_HOOK_CREATE_INDEX:-0}" == "1" ]]; then
    INDEX_FILE="$LOG_DIR/$DATE/forensic-index.jsonl"
    echo "{\"timestamp\":\"$TIMESTAMP\",\"hook_type\":\"$HOOK_TYPE\",\"tool_name\":\"$TOOL_NAME\",\"session_id\":\"$SESSION_ID\",\"file\":\"$FILEPATH\",\"forensic\":true}" >> "$INDEX_FILE"
fi

# Cleanup
find "$TARGET_DIR" -name "*.tmp.*" -mmin +5 -delete 2>/dev/null || true

exit 0