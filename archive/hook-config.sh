#!/bin/bash
# hook-config-dry.sh - DRY Configuration helper for Claude Code hooks

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS_FILE="$SCRIPT_DIR/.claude/settings.json"

# Hook type definitions - single source of truth
get_hook_types() {
    case "$1" in
        "basic") echo "PreToolUse,PostToolUse" ;;
        "extended") echo "PreToolUse,PostToolUse,UserPromptSubmit,Notification" ;;
        "all") echo "PreToolUse,PostToolUse,UserPromptSubmit,Notification,Stop,SubagentStop,PreCompact" ;;
        *) return 1 ;;
    esac
}

# Logger definitions - single source of truth
get_logger_path() {
    case "$1" in
        "universal") echo "$SCRIPT_DIR/universal-hook-logger.sh" ;;
        "forensic") echo "$SCRIPT_DIR/forensic-hook-logger.sh" ;;
        "forensic-jc") echo "$SCRIPT_DIR/forensic-hook-logger-jc.sh" ;;
        "forensic-fixed") echo "$SCRIPT_DIR/forensic-fixed.sh" ;;
        *) return 1 ;;
    esac
}

show_help() {
    cat << EOF
🔍 DRY Hook Configuration Helper

USAGE:
    $0 [COMMAND]

COMMANDS:
    enable <logger> <scope>   Enable hooks with specific logger and scope
    disable                   Disable all hook logging
    status                    Show current configuration
    test                      Test the logger
    cleanup                   Clean up old log files
    help                      Show this help

LOGGERS:
    universal      Basic universal logger (JSONL)
    forensic       Original forensic logger  
    forensic-jc    jc-enhanced forensic logger
    forensic-fixed FIXED jc-enhanced JSONL logger (recommended)

SCOPES:
    basic          PreToolUse, PostToolUse only
    extended       Basic + UserPromptSubmit, Notification
    all           All 7 hook types (includes Stop, SubagentStop, PreCompact)

EXAMPLES:
    $0 enable forensic-fixed extended    # Recommended setup
    $0 enable universal basic            # Minimal logging
    $0 enable forensic-fixed all         # Full forensic coverage
    $0 disable                           # Turn off all hooks
    $0 status                            # Check current setup

ENVIRONMENT VARIABLES:
    CLAUDE_HOOK_LOG_DIR         Directory for logs (default: ./hooks-debug)
    CLAUDE_HOOK_DISABLE         Set to "1" to disable logging
    CLAUDE_HOOK_FILTER_TOOLS    Comma-separated tool names to log
    CLAUDE_HOOK_MAX_SIZE        Max file size in bytes
    CLAUDE_HOOK_CREATE_INDEX    Set to "1" to create daily index files

EOF
}

# Core DRY function - generates hook configuration
create_hook_config() {
    local logger_name="$1"
    local scope="$2"
    local description="$3"
    
    # Validate inputs
    local logger_path=$(get_logger_path "$logger_name")
    if [[ $? -ne 0 ]]; then
        echo "❌ Unknown logger: $logger_name"
        echo "Available: universal, forensic, forensic-jc, forensic-fixed"
        return 1
    fi
    
    local hook_list=$(get_hook_types "$scope")
    if [[ $? -ne 0 ]]; then
        echo "❌ Unknown scope: $scope"
        echo "Available: basic, extended, all"
        return 1
    fi
    
    # Check if logger exists
    if [[ ! -f "$logger_path" ]]; then
        echo "❌ Logger not found: $logger_path"
        return 1
    fi
    
    echo "🔧 Enabling: $description"
    echo "   Logger: $logger_name ($logger_path)"
    echo "   Scope: $scope ($hook_list)"
    echo ""
    
    # Generate JSON programmatically
    echo '{' > "$SETTINGS_FILE"
    echo '  "hooks": {' >> "$SETTINGS_FILE"
    
    # Split hook types and create entries
    local first=true
    IFS=',' read -ra HOOKS <<< "$hook_list"
    for hook in "${HOOKS[@]}"; do
        if [[ "$first" == "false" ]]; then
            echo ',' >> "$SETTINGS_FILE"
        fi
        first=false
        
        cat << EOF >> "$SETTINGS_FILE"
    "$hook": [{
      "matcher": ".*",
      "hooks": [{
        "type": "command",
        "command": "$logger_path $hook"
      }]
    }]
EOF
    done
    
    echo '' >> "$SETTINGS_FILE"
    echo '  }' >> "$SETTINGS_FILE"
    echo '}' >> "$SETTINGS_FILE"
    
    echo "✅ Configuration updated: $SETTINGS_FILE"
    echo "   Hook types: $hook_list"
    echo ""
    echo "🔄 Restart Claude Code to apply changes."
}

# Predefined configurations for backwards compatibility
enable_universal_basic() {
    create_hook_config "universal" "basic" "Universal logging (basic scope)"
}

enable_universal_all() {
    create_hook_config "universal" "all" "Universal logging (all 7 hook types)"
}

enable_forensic_extended() {
    create_hook_config "forensic" "extended" "Forensic logging (extended scope)"
}

enable_forensic_jc_extended() {
    create_hook_config "forensic-jc" "extended" "jc-enhanced forensic logging"
}

enable_forensic_fixed_extended() {
    create_hook_config "forensic-fixed" "extended" "FIXED jc-enhanced JSONL logging (recommended)"
}

disable_hooks() {
    echo "🚫 Disabling all hook logging..."
    echo '{}' > "$SETTINGS_FILE"
    echo "✅ All hooks disabled"
    echo "🔄 Restart Claude Code to apply changes."
}

show_status() {
    echo "📊 Hook Configuration Status"
    echo "============================"
    echo ""
    
    if [[ -f "$SETTINGS_FILE" ]]; then
        echo "📁 Settings file: $SETTINGS_FILE"
        
        # Count hook types configured
        local hook_count=$(jq -r '.hooks | keys | length' "$SETTINGS_FILE" 2>/dev/null || echo "0")
        echo "🔧 Configured hook types: $hook_count"
        
        if [[ "$hook_count" -gt 0 ]]; then
            echo "📋 Active hooks:"
            jq -r '.hooks | keys[]' "$SETTINGS_FILE" 2>/dev/null | sed 's/^/   • /'
            
            echo ""
            echo "🛠️  Logger commands:"
            jq -r '.hooks | to_entries[] | "   • \(.key): \(.value[0].hooks[0].command)"' "$SETTINGS_FILE" 2>/dev/null
        fi
    else
        echo "❌ No settings file found: $SETTINGS_FILE"
    fi
    
    echo ""
    echo "🌍 Environment:"
    echo "   CLAUDE_HOOK_LOG_DIR: ${CLAUDE_HOOK_LOG_DIR:-./hooks-debug}"
    echo "   CLAUDE_HOOK_DISABLE: ${CLAUDE_HOOK_DISABLE:-0}"
    echo "   CLAUDE_HOOK_FILTER_TOOLS: ${CLAUDE_HOOK_FILTER_TOOLS:-<all>}"
    echo ""
    echo "📚 Available loggers:"
    for logger in universal forensic forensic-jc forensic-fixed; do
        local path=$(get_logger_path "$logger")
        if [[ -f "$path" ]]; then
            echo "   ✅ $logger: $path"
        else
            echo "   ❌ $logger: $path (missing)"
        fi
    done
    
    echo ""
    echo "🎯 Available scopes:"
    for scope in basic extended all; do
        local types=$(get_hook_types "$scope")
        echo "   • $scope: $types"
    done
}

test_logger() {
    echo "🧪 Testing hook logger..."
    
    local test_data='{"tool_name":"TestTool","session_id":"test-session","cwd":"'"$PWD"'"}'
    
    # Find current logger from settings
    local current_logger=$(jq -r '.hooks.PreToolUse[0].hooks[0].command // "none"' "$SETTINGS_FILE" 2>/dev/null)
    
    if [[ "$current_logger" != "none" && "$current_logger" != "null" ]]; then
        echo "🎯 Testing current logger: $current_logger"
        echo "$test_data" | $current_logger
        echo "✅ Test completed. Check hooks-debug/ directory for output."
    else
        echo "❌ No hooks configured. Use 'enable' command first."
        return 1
    fi
}

cleanup_logs() {
    local log_dir="${CLAUDE_HOOK_LOG_DIR:-./hooks-debug}"
    
    echo "🧹 Cleaning up old log files in: $log_dir"
    
    if [[ -d "$log_dir" ]]; then
        # Remove files older than 7 days
        find "$log_dir" -name "*.json*" -mtime +7 -delete 2>/dev/null || true
        
        # Remove empty directories
        find "$log_dir" -type d -empty -delete 2>/dev/null || true
        
        echo "✅ Cleanup completed"
    else
        echo "❌ Log directory not found: $log_dir"
    fi
}

# Main command handler
case "${1:-help}" in
    "enable")
        if [[ $# -eq 3 ]]; then
            create_hook_config "$2" "$3" "Custom configuration"
        elif [[ $# -eq 2 ]]; then
            # Assume 'extended' scope if not specified
            create_hook_config "$2" "extended" "Custom configuration (extended scope)"
        else
            echo "❌ Usage: $0 enable <logger> [<scope>]"
            echo "Example: $0 enable forensic-fixed extended"
            exit 1
        fi
        ;;
    "enable-universal")     enable_universal_all ;;        # Backwards compatibility
    "enable-tools")         enable_universal_basic ;;      # Backwards compatibility  
    "enable-forensic")      enable_forensic_extended ;;    # Backwards compatibility
    "enable-jc")           enable_forensic_jc_extended ;;  # Backwards compatibility
    "enable-fixed")        enable_forensic_fixed_extended ;; # Backwards compatibility
    "disable")             disable_hooks ;;
    "status")              show_status ;;
    "test")                test_logger ;;
    "cleanup")             cleanup_logs ;;
    "help"|*)              show_help ;;
esac