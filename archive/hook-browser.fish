#!/usr/bin/env fish
# hook-browser.fish - Interactive Claude Code hook log navigator
# Requires: fzf, gum, jq, bat (optional)

set -l LOG_DIR (test -n "$CLAUDE_HOOK_LOG_DIR"; and echo $CLAUDE_HOOK_LOG_DIR; or echo "./hooks-debug")

function show_help
    echo "🔍 Hook Browser - Interactive Claude Code Hook Log Navigator"
    echo ""
    echo "USAGE:"
    echo "  hook-browser.fish [COMMAND]"
    echo ""
    echo "COMMANDS:"
    echo "  browse     Interactive file browser (default)"
    echo "  sessions   Browse by session ID" 
    echo "  tools      Browse by tool type"
    echo "  recent     Show recent hook activity"
    echo "  search     Search hook content"
    echo "  stats      Show logging statistics"
    echo "  help       Show this help"
    echo ""
    echo "NAVIGATION:"
    echo "  ↑/↓       Navigate files"
    echo "  Enter     View file content"
    echo "  Tab       Preview in sidebar"
    echo "  Esc       Back/quit"
    echo ""
    echo "ENVIRONMENT:"
    echo "  CLAUDE_HOOK_LOG_DIR  Log directory (default: ./hooks-debug)"
end

function check_dependencies
    set -l missing
    
    if not command -v fzf >/dev/null
        set -a missing "fzf"
    end
    
    if not command -v gum >/dev/null
        set -a missing "gum"
    end
    
    if not command -v jq >/dev/null
        set -a missing "jq"
    end
    
    if test (count $missing) -gt 0
        echo "❌ Missing dependencies: $missing"
        echo ""
        echo "Install with:"
        echo "  brew install fzf gum jq bat"
        return 1
    end
    
    return 0
end

function format_file_info
    set -l filepath $argv[1]
    
    if not test -f "$filepath"
        return 1
    end
    
    # Extract info from first line (metadata)
    set -l meta (head -1 "$filepath" | jq -r '.meta // empty' 2>/dev/null)
    
    if test -z "$meta"
        return 1
    end
    
    set -l hook_type (echo "$meta" | jq -r '.hook_type // "unknown"')
    set -l tool_name (echo "$meta" | jq -r '.tool_name // "unknown"')
    set -l timestamp (echo "$meta" | jq -r '.timestamp // "unknown"')
    set -l session_id (echo "$meta" | jq -r '.session_id // "unknown"' | cut -c1-8)
    
    # Get file size
    set -l size (du -h "$filepath" | cut -f1)
    
    printf "%-12s %-20s %-8s %s [%s]\n" "$hook_type" "$tool_name" "$session_id" "$timestamp" "$size"
end

function browse_files
    if not test -d "$LOG_DIR"
        gum style --foreground 196 "❌ Log directory not found: $LOG_DIR"
        return 1
    end
    
    gum style --foreground 33 "🔍 Browsing hook logs in: $LOG_DIR"
    echo ""
    
    # Find all .jsonl files and format them
    set -l files (find "$LOG_DIR" -name "*.jsonl" -type f | sort -r)
    
    if test (count $files) -eq 0
        gum style --foreground 196 "No hook logs found"
        return 1
    end
    
    # Create formatted list for fzf
    set -l formatted_files
    for file in $files
        set -l info (format_file_info "$file")
        if test -n "$info"
            set -a formatted_files "$info|$file"
        end
    end
    
    # Use fzf to select file
    set -l selected (printf '%s\n' $formatted_files | \
        fzf --delimiter='|' \
            --with-nth=1 \
            --preview='echo {2} | xargs cat | head -20' \
            --preview-window='right:50%' \
            --header='Select hook log file (Tab for preview, Enter to view)' \
            --border \
            --height=80%)
    
    if test -n "$selected"
        set -l filepath (echo "$selected" | cut -d'|' -f2)
        view_hook_file "$filepath"
    end
end

function view_hook_file
    set -l filepath $argv[1]
    
    if not test -f "$filepath"
        gum style --foreground 196 "❌ File not found: $filepath"
        return 1
    end
    
    gum style --foreground 33 "📄 Viewing: $filepath"
    echo ""
    
    # Check if bat is available for syntax highlighting
    if command -v bat >/dev/null
        bat --style=numbers,changes --language=json "$filepath"
    else
        cat -n "$filepath"
    end
    
    echo ""
    gum confirm "View raw stdin data?" --default=false
    if test $status -eq 0
        echo ""
        gum style --foreground 33 "🔍 Raw stdin data:"
        tail -1 "$filepath" | jq -r '.data' | jq .
    end
end

function browse_by_sessions
    if not test -d "$LOG_DIR"
        gum style --foreground 196 "❌ Log directory not found: $LOG_DIR"
        return 1
    end
    
    # Get unique session IDs
    set -l sessions (find "$LOG_DIR" -name "*.jsonl" -exec head -1 {} \; | \
        jq -r '.meta.session_id // empty' 2>/dev/null | \
        sort | uniq -c | sort -nr)
    
    if test (count $sessions) -eq 0
        gum style --foreground 196 "No sessions found"
        return 1
    end
    
    gum style --foreground 33 "👤 Sessions by activity:"
    echo ""
    
    set -l selected_session (printf '%s\n' $sessions | \
        fzf --header='Select session ID' \
            --preview='echo "Session: {2}" | head -1' \
            --border)
    
    if test -n "$selected_session"
        set -l session_id (echo "$selected_session" | awk '{print $2}')
        show_session_files "$session_id"
    end
end

function show_session_files
    set -l session_id $argv[1]
    
    gum style --foreground 33 "📋 Files for session: $session_id"
    echo ""
    
    set -l session_files (find "$LOG_DIR" -name "*.jsonl" -exec grep -l "\"session_id\":\"$session_id\"" {} \;)
    
    if test (count $session_files) -eq 0
        gum style --foreground 196 "No files found for session: $session_id"
        return 1
    end
    
    # Format and display files for this session
    set -l formatted_files
    for file in $session_files
        set -l info (format_file_info "$file")
        if test -n "$info"
            set -a formatted_files "$info|$file"
        end
    end
    
    set -l selected (printf '%s\n' $formatted_files | \
        fzf --delimiter='|' \
            --with-nth=1 \
            --preview='echo {2} | xargs cat | head -10' \
            --header="Files for session: $session_id" \
            --border)
    
    if test -n "$selected"
        set -l filepath (echo "$selected" | cut -d'|' -f2)
        view_hook_file "$filepath"
    end
end

function show_recent_activity
    gum style --foreground 33 "⏰ Recent hook activity (last 50 files):"
    echo ""
    
    find "$LOG_DIR" -name "*.jsonl" -type f -printf '%T@ %p\n' | \
        sort -nr | head -50 | cut -d' ' -f2- | \
        while read -l file
            set -l info (format_file_info "$file")
            if test -n "$info"
                echo "$info"
            end
        end
end

function search_content
    set -l query (gum input --placeholder="Enter search term...")
    
    if test -z "$query"
        return 1
    end
    
    gum style --foreground 33 "🔎 Searching for: $query"
    echo ""
    
    set -l matches (find "$LOG_DIR" -name "*.jsonl" -exec grep -l "$query" {} \;)
    
    if test (count $matches) -eq 0
        gum style --foreground 196 "No matches found"
        return 1
    end
    
    echo "Found $query in "(count $matches)" files:"
    echo ""
    
    for file in $matches
        set -l info (format_file_info "$file")
        if test -n "$info"
            echo "  $info"
        end
    end
end

function show_stats
    gum style --foreground 33 "📊 Hook Logging Statistics"
    echo ""
    
    if not test -d "$LOG_DIR"
        gum style --foreground 196 "❌ Log directory not found: $LOG_DIR"
        return 1
    end
    
    set -l total_files (find "$LOG_DIR" -name "*.jsonl" | wc -l)
    set -l total_size (du -sh "$LOG_DIR" 2>/dev/null | cut -f1)
    
    echo "📁 Total files: $total_files"
    echo "💾 Total size: $total_size"
    echo ""
    
    echo "📅 Files by date:"
    find "$LOG_DIR" -name "*.jsonl" | \
        sed 's|.*\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\).*|\1|' | \
        sort | uniq -c | sort -r
    
    echo ""
    echo "🔧 Hook types:"
    find "$LOG_DIR" -name "*.jsonl" -exec head -1 {} \; | \
        jq -r '.meta.hook_type // "unknown"' 2>/dev/null | \
        sort | uniq -c | sort -nr
    
    echo ""
    echo "⚙️  Tool usage:"
    find "$LOG_DIR" -name "*.jsonl" -exec head -1 {} \; | \
        jq -r '.meta.tool_name // "unknown"' 2>/dev/null | \
        sort | uniq -c | sort -nr | head -10
end

# Main command handler
function main
    if not check_dependencies
        return 1
    end
    
    switch "$argv[1]"
        case "sessions"
            browse_by_sessions
        case "tools"
            browse_files  # For now, same as browse
        case "recent"
            show_recent_activity
        case "search"
            search_content
        case "stats"
            show_stats
        case "help"
            show_help
        case "*"
            browse_files  # Default action
    end
end

# Run main function with all arguments
main $argv