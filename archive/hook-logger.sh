#!/bin/bash

# Claude Code Hook Environment Logger
# Logs all environment data when hook executes

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/Users/bdmorin/src/claude-hooks/hook-execution.$(date '+%Y%m%d%H%M%S').log"

echo "=================================" >> "$LOG_FILE"
echo "Hook Execution: $TIMESTAMP" >> "$LOG_FILE"
echo "=================================" >> "$LOG_FILE"

echo "--- COMMAND LINE ARGUMENTS ---" >> "$LOG_FILE"
echo "Number of args: $#" >> "$LOG_FILE"
for i in "$@"; do
    echo "ARG: $i" >> "$LOG_FILE"
done

echo "" >> "$LOG_FILE"
echo "--- ENVIRONMENT VARIABLES ---" >> "$LOG_FILE"
printenv >> "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "--- STDIN DATA ---" >> "$LOG_FILE"
# Read stdin and capture it
stdin_data=$(cat)
echo "$stdin_data" >> "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "--- STDIN PARSED (if JSON) ---" >> "$LOG_FILE"
if command -v jq >/dev/null 2>&1; then
    echo "$stdin_data" | jq . >> "$LOG_FILE" 2>/dev/null || echo "Not valid JSON" >> "$LOG_FILE"
else
    echo "jq not available for JSON parsing" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "--- WORKING DIRECTORY ---" >> "$LOG_FILE"
echo "PWD: $(pwd)" >> "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "--- PROCESS INFO ---" >> "$LOG_FILE"
echo "Timestamp: $(date -u)"
echo "PID: $$" >> "$LOG_FILE"
echo "PPID: $PPID" >> "$LOG_FILE"
echo "User: $(whoami)" >> "$LOG_FILE"
echo "Script: $0"  >> "$LOG_FILE"
echo "Shell: $SHELL"  >> "$LOG_FILE"
echo "Current Directory: $PWD" >> "$LOG_FILE"
echo "Hostname: $HOSTNAME" >> "$LOG_FILE"
echo "set:" >> "$LOG_FILE"
set  >> "$LOG_FILE"
echo "ps -fp:" >>"$LOG_FILE"
ps -fp $$  >> "$LOG_FILE"
echo "lsof:" >>"$LOG_FILE"
lsof -p $$  >> "$LOG_FILE"
echo "=================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Return success to not block Claude Code
exit 0
