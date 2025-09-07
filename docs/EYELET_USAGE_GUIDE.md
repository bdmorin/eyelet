# Eyelet Usage Guide for Local Development

## What is Eyelet?

Eyelet is a hook orchestration system for Claude Code that captures and logs ALL AI agent interactions. It provides comprehensive monitoring, templating, and analytics for AI development workflows.

## Installation & Setup

### Quick Install (Recommended)
```bash
# Install and configure everything with auto-updates
uvx eyelet@latest configure install-all --autoupdate

# Enable SQLite logging for better performance
uvx eyelet@latest configure logging --format sqlite

# Verify installation
uvx eyelet@latest doctor
```

### Global Installation (Alternative)
```bash
# Install globally with pipx
pipx install eyelet

# Then use without uvx prefix
eyelet doctor
eyelet configure install-all --autoupdate
```

## Core Commands

### 1. Configuration & Setup
```bash
# Install all hooks with auto-updates
uvx eyelet@latest configure install-all --autoupdate

# Configure logging format (json, sqlite, or both)
uvx eyelet@latest configure logging --format sqlite,json

# Check configuration health
uvx eyelet@latest doctor

# Validate Claude settings
uvx eyelet@latest validate settings
```

### 2. Monitoring & Logs
```bash
# View recent logs
uvx eyelet@latest logs --tail 20

# Follow logs in real-time
uvx eyelet@latest logs --follow

# Query SQLite database
uvx eyelet@latest query search --text "error"
uvx eyelet@latest query summary --last 24h
uvx eyelet@latest query errors --last 1h
```

### 3. Recall Feature (Search Conversations)
```bash
# Search Claude Code conversations
uvx eyelet@latest recall "search term"

# Filter by tool usage
uvx eyelet@latest recall --tool Bash "command"

# Filter by time
uvx eyelet@latest recall --since 24h "error"

# Limit results
uvx eyelet@latest recall --limit 10 "function"
```

### 4. Template Management
```bash
# List available templates
uvx eyelet@latest template list

# Install a template
uvx eyelet@latest template install universal-logger

# Show template details
uvx eyelet@latest template show universal-logger
```

### 5. Discovery
```bash
# Discover available hooks and tools
uvx eyelet@latest discover

# Show specific hook types
uvx eyelet@latest discover --type PreToolUse
```

## Integration with mise

Add to your project's `.mise.toml`:

```toml
[tools]
python = "3.11"

[tasks.hooks-install]
description = "Install eyelet hooks"
run = "uvx eyelet@latest configure install-all --autoupdate"

[tasks.hooks-doctor]
description = "Check eyelet configuration"
run = """
uvx eyelet@latest doctor
echo "📌 Version: $(uvx eyelet@latest --version)"
"""

[tasks.hooks-logs]
run = "uvx eyelet@latest logs --tail 20"

# Shortcuts
[tasks.hd]
alias = "hooks-doctor"
```

Then use:
```bash
mise run hooks-install
mise run hd  # Check configuration
```

## Understanding Hook Logs

Eyelet captures these hook types:
- **PreToolUse/PostToolUse**: Tool execution monitoring
- **UserPromptSubmit**: User input validation
- **Stop/SubagentStop**: Session completion
- **PreCompact**: Context management
- **Notification**: User interactions

Logs are stored in:
```
~/.eyelet/hooks/              # Central hooks directory (default)
~/.eyelet/eyelet.db          # SQLite database
./eyelet-hooks/              # Project-specific logs (optional)
```

## Updating Eyelet

```bash
# Always use @latest for newest version
uvx eyelet@latest [command]

# Or force reinstall with uv tool
uv tool install --reinstall eyelet@latest

# Check current version
uvx eyelet@latest --version
```

## Common Use Cases

### 1. Debug AI Agent Behavior
```bash
# Search for specific tool usage
uvx eyelet@latest query search --tool Bash --text "git"

# View error patterns
uvx eyelet@latest query errors --last 24h
```

### 2. Analyze Session Activity
```bash
# Get session summary
uvx eyelet@latest query summary

# View specific session
uvx eyelet@latest query session <session-id>
```

### 3. Monitor Real-Time Activity
```bash
# Watch hooks as they execute
uvx eyelet@latest logs --follow

# Filter by hook type
uvx eyelet@latest logs --type PreToolUse --follow
```

### 4. Search Historical Conversations
```bash
# Find conversations about specific topics
uvx eyelet@latest recall "database migration"

# Find when specific commands were used
uvx eyelet@latest recall --tool Bash "docker"
```

## Troubleshooting

### If hooks aren't logging:
1. Run `uvx eyelet@latest doctor`
2. Check for unpinned versions warning
3. Reinstall with: `uvx eyelet@latest configure install-all --autoupdate`

### If SQLite isn't working:
1. Enable it: `uvx eyelet@latest configure logging --format sqlite`
2. Check database: `ls -la ~/.eyelet/eyelet.db`

### If updates aren't working:
1. Always use `@latest`: `uvx eyelet@latest`
2. Or force reinstall: `uv tool install --reinstall eyelet@latest`

## Important Notes

- **Designed for uvx**: Eyelet works best with `uvx eyelet@latest`
- **Auto-updates**: Use `--autoupdate` flag when installing hooks
- **Performance**: SQLite logging is faster than JSON for queries
- **Privacy**: All logs are local - nothing is sent externally

## Environment Variables

```bash
# Optional configuration
export EYELET_LOG_LEVEL=INFO
export EYELET_HOOKS_DIR=~/.eyelet/hooks
```

## Quick Reference Card

```bash
# Essential Commands
uvx eyelet@latest configure install-all --autoupdate  # Setup
uvx eyelet@latest doctor                              # Health check
uvx eyelet@latest logs --tail 20                      # View logs
uvx eyelet@latest query summary                       # Statistics
uvx eyelet@latest recall "search"                     # Search conversations
uvx eyelet@latest --version                           # Check version
```

## Support

- GitHub: https://github.com/bdmorin/eyelet
- Issues: https://github.com/bdmorin/eyelet/issues
- PyPI: https://pypi.org/project/eyelet/