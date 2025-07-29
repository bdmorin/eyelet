# Eyelet Quick Start Guide

Get up and running with Eyelet in under 5 minutes!

## Installation

```bash
# Install with uvx (recommended)
uvx eyelet

# Or with pipx
pipx install eyelet

# Or from source
git clone https://github.com/bdmorin/eyelet
cd eyelet
uv pip install -e .
```

## Universal Hook Logging (Recommended First Step!)

Install comprehensive logging for ALL Claude Code hooks with one command:

```bash
uvx eyelet configure install-all
```

This will:
- ✅ Configure hooks for PreToolUse, PostToolUse, UserPromptSubmit, etc.
- ✅ Log all hook data to `./eyelet-hooks/` directory
- ✅ Organize logs by hook type, tool, and date
- ✅ Capture complete context and payloads

## What Gets Logged?

After running `install-all`, every Claude Code action will be logged:

```
./eyelet-hooks/
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
ls -la ./eyelet-hooks/

# Find recent Bash commands
find ./eyelet-hooks/PreToolUse/Bash -name "*.json" -mtime -1

# Search for specific content
grep -r "git push" ./eyelet-hooks/

# Pretty-print a log file
cat ./eyelet-hooks/PreToolUse/Bash/2025-01-20/*.json | jq .
```

## Basic Commands

```bash
# Launch the TUI
uvx eyelet

# List current hooks
uvx eyelet configure list

# View recent executions (once SQLite is implemented)
uvx eyelet logs --tail 20

# Install a specific template
uvx eyelet template install bash-validator

# Get help on any command
uvx eyelet configure --help
uvx eyelet template --help
```

## Example: Security Monitoring

Monitor all shell commands executed by Claude Code:

```bash
# Watch for new Bash commands in real-time
watch -n 1 'find ./eyelet-hooks/PreToolUse/Bash -name "*.json" -mmin -5 | tail -10'

# Find all rm commands
find ./eyelet-hooks -name "*.json" -exec grep -l "rm " {} \;

# Analyze command frequency
find ./eyelet-hooks/PreToolUse/Bash -name "*.json" | \
  xargs jq -r '.input_data.tool_input.command' | \
  sort | uniq -c | sort -nr
```

## Next Steps

1. **Explore the logs** - Check `./eyelet-hooks/` to see what Claude Code is doing
2. **Configure custom hooks** - Use `eyelet configure add` for specific needs
3. **Install templates** - Try `eyelet template list` to see available options
4. **Set up completion** - Run `eyelet completion install` for tab completion

## Troubleshooting

### Logs not appearing?
```bash
# Verify hooks are installed
uvx eyelet configure list

# Reinstall if needed
uvx eyelet configure install-all --force
```

### Permission issues?
```bash
# Check directory permissions
ls -la .claude/
chmod 755 .claude/settings.json
```

### Need to clear all hooks?
```bash
uvx eyelet configure clear --force
```

## Getting Help

```bash
# General help
uvx eyelet --help

# Command-specific help
eyelet configure --help
eyelet configure install-all --help

# View documentation
uvx eyelet help
```

Welcome aboard! You're now logging every Claude Code action for complete visibility. ⚓