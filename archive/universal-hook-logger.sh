#!/bin/bash
# universal-hook-logger.sh - Ultra-fast Claude Code hook debugging
# Captures ALL hook types with organized directory structure and JSONL format
set -euo pipefail

# Hook type passed as first argument
HOOK_TYPE="${1:-unknown}"

# High-precision timestamps
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%6NZ")
DATE=$(date -u +"%Y-%m-%d") 
TIME_FILE=$(date -u +"%H:%M:%S_UTC")

# Configuration via environment variables
LOG_DIR="${CLAUDE_HOOK_LOG_DIR:-./hooks-debug}"
DISABLE_LOGGING="${CLAUDE_HOOK_DISABLE:-0}"
MAX_FILE_SIZE="${CLAUDE_HOOK_MAX_SIZE:-1048576}"  # 1MB default

# Exit early if logging disabled
[[ "$DISABLE_LOGGING" == "1" ]] && exit 0

# Read all stdin data (JSON from Claude Code)
STDIN_DATA=""
while IFS= read -r line; do
    STDIN_DATA+="$line"$'\n'
done

# Remove trailing newline
STDIN_DATA="${STDIN_DATA%$'\n'}"

# Fast JSON extraction with error handling
extract_json_field() {
    echo "$STDIN_DATA" | jq -r ".$1 // \"unknown\"" 2>/dev/null || echo "unknown"
}

# Extract key fields
TOOL_NAME=$(extract_json_field "tool_name")
SESSION_ID=$(extract_json_field "session_id")
CWD=$(extract_json_field "cwd")

# Handle different hook types that might not have tool_name
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

# Sanitize tool name for filesystem (remove special chars)
SAFE_TOOL_NAME=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9_-]/_/g' | sed 's/__*/_/g')

# Create organized directory structure  
TARGET_DIR="$LOG_DIR/$DATE/$HOOK_TYPE/$SAFE_TOOL_NAME"
mkdir -p "$TARGET_DIR"

# Generate unique filename: YYYY-MM-DD.HH:MM:SS_TZ.description.jsonl
DESCRIPTION=$(echo "$TOOL_NAME" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-20)
FILENAME="$DATE.$TIME_FILE.$DESCRIPTION.jsonl"
FILEPATH="$TARGET_DIR/$FILENAME"

# Check for tool filtering
if [[ -n "${CLAUDE_HOOK_FILTER_TOOLS:-}" ]]; then
    # Only log if tool is in filter list
    if [[ ",$CLAUDE_HOOK_FILTER_TOOLS," != *",$TOOL_NAME,"* ]]; then
        exit 0
    fi
fi

# Truncate stdin data if too large
if [[ ${#STDIN_DATA} -gt $MAX_FILE_SIZE ]]; then
    STDIN_DATA="${STDIN_DATA:0:$MAX_FILE_SIZE}... [TRUNCATED]"
fi

# Create JSONL log entry with atomic write (2 lines)
TEMP_FILE="$FILEPATH.tmp.$$"

{
    # Line 1: Metadata (no raw_stdin)
    echo '{'
    echo '  "meta": {'
    echo "    \"hook_type\": \"$HOOK_TYPE\","
    echo "    \"timestamp\": \"$TIMESTAMP\","
    echo "    \"log_file\": \"$FILEPATH\","
    echo "    \"session_id\": \"$SESSION_ID\","
    echo "    \"tool_name\": \"$TOOL_NAME\","
    echo "    \"pid\": $$,"
    echo "    \"hostname\": \"$(hostname)\""
    echo '  },'
    echo '  "parsed": {'
    echo "    \"session_id\": \"$SESSION_ID\","
    echo "    \"tool_name\": \"$TOOL_NAME\","
    echo "    \"cwd\": \"$CWD\","
    echo "    \"hook_event_name\": \"$HOOK_TYPE\""
    echo '  },'
    echo '  "environment": {'
    echo "    \"PWD\": \"${PWD:-}\","
    echo "    \"CLAUDE_PROJECT_DIR\": \"${CLAUDE_PROJECT_DIR:-}\","
    echo "    \"CLAUDE_CODE_ENTRYPOINT\": \"${CLAUDE_CODE_ENTRYPOINT:-}\","
    echo "    \"USER\": \"${USER:-}\","
    echo "    \"SHELL\": \"${SHELL:-}\""
    echo '  },'
    echo '  "performance": {'
    echo "    \"log_timestamp\": \"$TIMESTAMP\","
    echo "    \"data_size_bytes\": ${#STDIN_DATA}"
    echo '  }'
    echo '}'
    
    # Line 2: Raw stdin data (unwrapped)
    echo "$STDIN_DATA"
} > "$TEMP_FILE"

# Atomic move to final location
mv "$TEMP_FILE" "$FILEPATH" 

# Optional: Create daily index entry
if [[ "${CLAUDE_HOOK_CREATE_INDEX:-0}" == "1" ]]; then
    INDEX_FILE="$LOG_DIR/$DATE/index.jsonl"
    echo "{\"timestamp\":\"$TIMESTAMP\",\"hook_type\":\"$HOOK_TYPE\",\"tool_name\":\"$TOOL_NAME\",\"session_id\":\"$SESSION_ID\",\"file\":\"$FILEPATH\"}" >> "$INDEX_FILE"
fi

# Cleanup old temp files (failsafe)
find "$TARGET_DIR" -name "*.tmp.*" -mmin +5 -delete 2>/dev/null || true

# Always exit successfully to never block Claude Code
exit 0