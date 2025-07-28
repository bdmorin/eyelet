# Universal Hook Handler Guide

The Universal Hook Handler is Rigging's comprehensive logging system that captures EVERY hook event from Claude Code, providing complete visibility into AI agent behavior.

## Overview

The handler logs all hook events to a structured directory system (`./hms-hooks/`), creating a complete audit trail of AI agent actions. This is invaluable for:

- Debugging agent behavior
- Understanding tool usage patterns
- Security auditing
- Performance analysis
- Workflow development

## Quick Installation

```bash
# Install universal logging for ALL hooks
rigging configure install-all

# Or install for user-level (all projects)
rigging configure install-all --scope user
```

This single command configures Claude Code to send every hook event to Rigging's universal handler.

## Directory Structure

Logs are organized in a logical hierarchy:

```
./hms-hooks/
├── PreToolUse/           # Before tool execution
│   ├── Bash/            # Organized by tool
│   │   └── 2025-07-28/  # Daily directories
│   │       └── 20250728_133300_236408_PreToolUse_Bash.json
│   ├── Read/
│   ├── Write/
│   └── .../
├── PostToolUse/          # After tool execution
│   └── {tool}/
│       └── {date}/
├── UserPromptSubmit/     # User interactions
│   └── {date}/
├── Notification/         # UI notifications
├── Stop/                 # Session completions
├── SubagentStop/         # Subagent completions
└── PreCompact/           # Context management
    ├── manual/
    └── auto/
```

## Log File Format

Each log file contains comprehensive data:

```json
{
  "timestamp": "2025-07-28T13:33:00.236408",
  "timestamp_unix": 1753727580.236408,
  "hook_type": "PreToolUse",
  "tool_name": "Bash",
  "session_id": "session-abc123",
  "transcript_path": "/path/to/transcript.md",
  "cwd": "/current/working/directory",
  "environment": {
    "python_version": "3.11.5",
    "platform": "darwin",
    "rigging_version": "0.1.0",
    "env_vars": {
      "CLAUDE_CODE_SSE_PORT": "62007",
      "CLAUDE_CODE_ENTRYPOINT": "cli"
    }
  },
  "input_data": {
    // Complete hook payload from Claude Code
  },
  "metadata": {
    "log_file": "/path/to/this/log.json",
    "log_dir": "/path/to/log/directory",
    "project_dir": "/project/root"
  }
}
```

## Hook Types Captured

### Tool Hooks
- **PreToolUse**: Captures tool inputs before execution
- **PostToolUse**: Captures tool outputs after execution

Supported tools:
- Bash (shell commands)
- Read/Write/Edit (file operations)
- Grep/Glob (search operations)
- WebFetch/WebSearch (network operations)
- Task (subagent operations)

### Lifecycle Hooks
- **UserPromptSubmit**: User prompts before processing
- **Notification**: UI notifications and idle events
- **Stop**: Main agent session completion
- **SubagentStop**: Subagent task completion
- **PreCompact**: Context window management (manual/auto)

## Usage Examples

### Basic Installation
```bash
# Install for current project
rigging configure install-all

# Force reinstall (overwrites existing hooks)
rigging configure install-all --force
```

### Viewing Logs
```bash
# Browse log directory
ls -la ./hms-hooks/

# Find recent Bash commands
find ./hms-hooks/PreToolUse/Bash -name "*.json" -mtime -1

# Search for specific content
grep -r "rm -rf" ./hms-hooks/PreToolUse/Bash/
```

### Analyzing Logs
```python
import json
from pathlib import Path

# Read all PreToolUse Bash logs
hms_dir = Path("./hms-hooks")
bash_logs = hms_dir.glob("PreToolUse/Bash/**/*.json")

for log_file in bash_logs:
    with open(log_file) as f:
        data = json.load(f)
        command = data["input_data"]["tool_input"]["command"]
        print(f"{data['timestamp']}: {command}")
```

## Configuration Details

The `install-all` command creates hooks with:
- **Handler**: `rigging execute --log-only`
- **Matchers**: 
  - PreToolUse/PostToolUse: `.*` (wildcard - all tools)
  - PreCompact: `manual` and `auto`
  - Others: No matcher required

## Performance Considerations

- **Non-blocking**: Always returns success (exit 0)
- **Fast writes**: JSON files are written quickly
- **No external dependencies**: Pure filesystem operations
- **Automatic organization**: Daily directories prevent folder bloat

## Security & Privacy

- **Local only**: All logs stay on your machine
- **No network calls**: Pure filesystem logging
- **Gitignored**: `hms-hooks/` is in .gitignore by default
- **Sensitive data**: Be aware that logs may contain sensitive information

## Troubleshooting

### Logs not appearing
1. Check hooks are installed: `rigging configure list`
2. Verify rigging is in PATH: `which rigging`
3. Check permissions: `ls -la ./hms-hooks/`

### Large log directories
```bash
# Find and remove logs older than 7 days
find ./hms-hooks -name "*.json" -mtime +7 -delete

# Check disk usage
du -sh ./hms-hooks/
```

### Parsing errors
If Claude Code sends malformed JSON, check:
- `./hms-hooks/parse_error/` directory
- Look for `error` field in log files

## Advanced Usage

### Custom Workflows
After logging, you can trigger workflows:
```bash
rigging configure add --workflow my-validator
```

### Real-time Monitoring
```bash
# Watch for new logs
watch -n 1 'find ./hms-hooks -name "*.json" -mmin -5 | tail -20'
```

### Integration with Analysis Tools
Export to various formats:
```bash
# Convert to CSV for spreadsheet analysis
rigging logs export --format csv --output hooks.csv

# Stream to monitoring systems
tail -f ./hms-hooks/**/*.json | jq '.hook_type'
```

## Best Practices

1. **Regular Cleanup**: Set up log rotation to prevent disk bloat
2. **Security Review**: Audit logs don't contain secrets
3. **Performance Monitoring**: Check log sizes periodically
4. **Backup Important Logs**: Archive interesting sessions
5. **Privacy Awareness**: Remember logs contain all agent activity

## Future Enhancements

Planned features:
- Log compression and rotation
- Real-time log streaming
- Built-in analysis tools
- Webhook notifications
- Encrypted logging option