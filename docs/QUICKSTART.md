# Rigging Quick Start Guide

Get up and running with Rigging in under 5 minutes!

## Installation

```bash
# Install with uvx (recommended)
uvx --from rigging-cli rigging

# Or with pipx
pipx install rigging-cli

# Or from source
git clone https://github.com/bdmorin/rigging-cli
cd rigging-cli
uv pip install -e .
```

## Universal Hook Logging (Recommended First Step!)

Install comprehensive logging for ALL Claude Code hooks with one command:

```bash
uvx --from rigging-cli rigging configure install-all
```

This will:
- ✅ Configure hooks for PreToolUse, PostToolUse, UserPromptSubmit, etc.
- ✅ Log all hook data to `./hms-hooks/` directory
- ✅ Organize logs by hook type, tool, and date
- ✅ Capture complete context and payloads

## What Gets Logged?

After running `install-all`, every Claude Code action will be logged:

```
./hms-hooks/
├── PreToolUse/
│   ├── Bash/          # Before shell commands
│   ├── Read/          # Before file reads
│   └── Write/         # Before file writes
├── PostToolUse/       # After tool executions
├── UserPromptSubmit/  # User interactions
├── Stop/              # Session completions
└── PreCompact/        # Context management
```

Each JSON log contains:
- Timestamp and session ID
- Complete input/output data
- Environment variables
- Tool parameters and results
- Error information (if any)

## Viewing Your Logs

```bash
# Browse the log directory
ls -la ./hms-hooks/

# Find recent Bash commands
find ./hms-hooks/PreToolUse/Bash -name "*.json" -mtime -1

# Search for specific content
grep -r "git push" ./hms-hooks/

# Pretty-print a log file
cat ./hms-hooks/PreToolUse/Bash/2025-01-20/*.json | jq .
```

## Basic Commands

```bash
# Launch the TUI
uvx --from rigging-cli rigging

# List current hooks
uvx --from rigging-cli uvx --from rigging-cli rigging configure list

# View recent executions (once SQLite is implemented)
uvx --from rigging-cli rigging logs --tail 20

# Install a specific template
uvx --from rigging-cli rigging template install bash-validator

# Get help on any command
uvx --from rigging-cli rigging configure --help
uvx --from rigging-cli rigging template --help
```

## Example: Security Monitoring

Monitor all shell commands executed by Claude Code:

```bash
# Watch for new Bash commands in real-time
watch -n 1 'find ./hms-hooks/PreToolUse/Bash -name "*.json" -mmin -5 | tail -10'

# Find all rm commands
find ./hms-hooks -name "*.json" -exec grep -l "rm " {} \;

# Analyze command frequency
find ./hms-hooks/PreToolUse/Bash -name "*.json" | \
  xargs jq -r '.input_data.tool_input.command' | \
  sort | uniq -c | sort -nr
```

## Next Steps

1. **Explore the logs** - Check `./hms-hooks/` to see what Claude Code is doing
2. **Configure custom hooks** - Use `rigging configure add` for specific needs
3. **Install templates** - Try `rigging template list` to see available options
4. **Set up completion** - Run `rigging completion install` for tab completion

## Troubleshooting

### Logs not appearing?
```bash
# Verify hooks are installed
uvx --from rigging-cli rigging configure list

# Reinstall if needed
uvx --from rigging-cli rigging configure install-all --force
```

### Permission issues?
```bash
# Check directory permissions
ls -la .claude/
chmod 755 .claude/settings.json
```

### Need to clear all hooks?
```bash
uvx --from rigging-cli rigging configure clear --force
```

## Getting Help

```bash
# General help
uvx --from rigging-cli rigging --help

# Command-specific help
rigging configure --help
uvx --from rigging-cli rigging configure install-all --help

# View documentation
uvx --from rigging-cli rigging help
```

Welcome aboard! You're now logging every Claude Code action for complete visibility. ⚓