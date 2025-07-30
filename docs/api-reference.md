# Eyelet API Reference

⚓ **Complete API documentation for Eyelet - Hook Orchestration for AI Agents**

## Table of Contents

1. [CLI Command Reference](#cli-command-reference)
2. [Hook Event API](#hook-event-api)
3. [Configuration API](#configuration-api)
4. [Python API](#python-api)
5. [Template API](#template-api)
6. [Logging API](#logging-api)
7. [Error Codes and Messages](#error-codes-and-messages)

---

## CLI Command Reference

### Global Options

All commands support these global options:

| Option | Description |
|--------|-------------|
| `--config-dir PATH` | Set configuration directory (default: current directory) |
| `--version` | Show version information |
| `-h, --help` | Show help message |

### eyelet

Launch the interactive TUI when run without arguments.

```bash
eyelet  # Launch TUI
```

### eyelet configure

Manage hook configurations for your project.

#### Subcommands

##### configure list

List current hook configuration.

```bash
eyelet configure list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Configuration scope (default: project) |

##### configure add

Add a new hook interactively.

```bash
eyelet configure add [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Configuration scope (default: project) |

##### configure remove

Remove a hook by ID.

```bash
eyelet configure remove HOOK_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Configuration scope (default: project) |

##### configure enable

Enable a hook.

```bash
eyelet configure enable HOOK_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Configuration scope (default: project) |

##### configure disable

Disable a hook.

```bash
eyelet configure disable HOOK_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Configuration scope (default: project) |

##### configure clear

Clear all hooks (with confirmation).

```bash
eyelet configure clear [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Configuration scope (default: project) |
| `--force` | Clear without confirmation |

##### configure install-all

Install universal logging for ALL hooks.

```bash
eyelet configure install-all [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Configuration scope (default: project) |
| `--force` | Overwrite existing hooks without confirmation |
| `--dev` | Use local development wheel instead of public uvx |

This command installs comprehensive hook configuration that logs every Claude Code hook:
- PreToolUse: All tools
- PostToolUse: All tools  
- UserPromptSubmit
- Notification
- Stop
- SubagentStop
- PreCompact (manual and auto)

##### configure logging

Configure logging settings.

```bash
eyelet configure logging [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--format FORMAT` | Logging format(s) - comma-separated (json, sqlite, json,sqlite) |
| `--scope [global\|project\|both]` | Logging scope |
| `--enabled/--disabled` | Enable or disable logging |
| `--global` | Configure global settings instead of project |

Examples:
```bash
# Show current settings
eyelet configure logging

# Enable SQLite logging
eyelet configure logging --format sqlite

# Use both formats globally
eyelet configure logging --format json,sqlite --scope global --global

# Disable logging temporarily
eyelet configure logging --disabled
```

### eyelet validate

Validate configurations.

#### Subcommands

##### validate settings

Validate Claude settings.json against schema.

```bash
eyelet validate settings [SETTINGS_FILE] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--schema PATH` | Path to JSON schema file |

##### validate hooks

Validate all hooks in current configuration.

```bash
eyelet validate hooks
```

### eyelet execute

Execute as a hook endpoint (called by Claude Code).

```bash
eyelet execute [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--workflow WORKFLOW` | Workflow to execute |
| `--log-only` | Only log, no processing |
| `--log-result` | Log result after execution |
| `--debug` | Enable debug output |
| `--no-logging` | Disable all logging |
| `--legacy-log` | Use legacy JSON file logging only |

This command reads JSON from stdin and processes according to configuration.

### eyelet template

Manage hook templates.

#### Subcommands

##### template list

List available templates.

```bash
eyelet template list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--category CATEGORY` | Filter by category |

##### template show

Show template details.

```bash
eyelet template show TEMPLATE_ID
```

##### template install

Install a template.

```bash
eyelet template install TEMPLATE_ID [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--scope [project\|user]` | Installation scope (default: project) |
| `--var KEY=VALUE` | Set template variables (can be used multiple times) |

##### template create

Create a new template interactively.

```bash
eyelet template create
```

##### template export

Export a template.

```bash
eyelet template export TEMPLATE_ID OUTPUT_FILE
```

##### template import

Import a template file.

```bash
eyelet template import-template TEMPLATE_FILE
```

### eyelet query

Query and analyze hook logs.

#### Subcommands

##### query search

Search hook logs with filters.

```bash
eyelet query search [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--hook-type TYPE` | Filter by hook type (e.g., PreToolUse) |
| `--tool TOOL` | Filter by tool name (e.g., Bash) |
| `--session SESSION` | Filter by session ID |
| `--since TIME` | Start time (e.g., "1h", "24h", "2024-01-01") |
| `--status STATUS` | Filter by status (success, error) |
| `--branch BRANCH` | Filter by git branch |
| `--errors-only` | Show only errors |
| `--limit N` | Maximum results (default: 20) |
| `--format [table\|json\|raw]` | Output format (default: table) |

##### query summary

Show summary statistics of hook activity.

```bash
eyelet query summary [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--since TIME` | Time period (default: "24h") |

##### query errors

Show recent errors.

```bash
eyelet query errors [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit N` | Number of errors to show (default: 10) |

##### query session

Show timeline for a specific session.

```bash
eyelet query session SESSION_ID
```

##### query grep

Search for a term in all log data.

```bash
eyelet query grep SEARCH_TERM [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit N` | Maximum results (default: 20) |

### eyelet doctor

Diagnose configuration and system health.

```bash
eyelet doctor [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--fix` | Automatically fix issues where possible |
| `--verbose` | Show detailed diagnostic information |

Checks for:
- Claude Code integration status
- Configuration file validity
- Database accessibility
- Directory permissions
- Hook command consistency

### eyelet completion

Manage shell completion for Eyelet.

#### Subcommands

##### completion install

Install shell completion.

```bash
eyelet completion install [SHELL] [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--path PATH` | Path to install completion script |

Supported shells: bash, zsh, fish, powershell

##### completion show

Show completion script for a shell.

```bash
eyelet completion show SHELL
```

##### completion status

Check completion installation status.

```bash
eyelet completion status
```

### eyelet status

Show current configuration and status.

```bash
eyelet status
```

### eyelet tui

Launch the Textual TUI.

```bash
eyelet tui
```

### eyelet discover

Discover available hooks (implementation pending).

```bash
eyelet discover
```

### eyelet logs

View execution logs (implementation pending).

```bash
eyelet logs [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--tail N` | Show last N log entries |

---

## Hook Event API

### Event Data Structures

All hook events receive a JSON payload via stdin with these common fields:

```json
{
  "hook_event_name": "PreToolUse",  // Hook type
  "session_id": "uuid",              // Session identifier
  "transcript_path": "/path/to/transcript",
  "cwd": "/current/working/directory",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Hook Types

#### PreToolUse / PostToolUse

Additional fields for tool hooks:

```json
{
  "tool_name": "Bash",  // Tool being invoked
  "tool_input": {       // Tool-specific input
    "command": "ls -la" // For Bash tool
  }
}
```

#### UserPromptSubmit

Additional fields:

```json
{
  "prompt": "User's input message"
}
```

#### Notification

Additional fields:

```json
{
  "notification_type": "type",
  "message": "Notification message"
}
```

#### Stop / SubagentStop

Additional fields:

```json
{
  "reason": "Stop reason",
  "final_state": {}  // Session state information
}
```

#### PreCompact

Additional fields:

```json
{
  "compact_type": "manual" | "auto",
  "context_size": 1000,
  "threshold": 0.8
}
```

### Environment Variables

These environment variables are available to hook commands:

| Variable | Description |
|----------|-------------|
| `CLAUDE_SESSION_ID` | Current session ID |
| `CLAUDE_HOOK_TYPE` | Hook type being executed |
| `CLAUDE_TOOL_NAME` | Tool name (for tool hooks) |
| `CLAUDE_TRANSCRIPT_PATH` | Path to conversation transcript |
| `CLAUDE_CWD` | Current working directory |
| `EYELET_LOG_PATH` | Path to Eyelet log directory |
| `EYELET_CONFIG_DIR` | Eyelet configuration directory |

### Exit Codes

Hook commands should use these exit codes:

| Code | Meaning | Effect |
|------|---------|--------|
| 0 | Success | Continue normally |
| 1 | General error | Log error, continue |
| 2 | Block action | Prevent tool execution (PreToolUse only) |
| 3+ | Custom error | Log error with code, continue |

---

## Configuration API

### eyelet.yaml Schema

Project-specific Eyelet configuration:

```yaml
# Logging configuration
logging:
  format: "sqlite"  # json, sqlite, or both
  enabled: true
  scope: "project"  # project, global, or both
  global_path: "~/.claude/eyelet-logging"
  project_path: ".eyelet-logging"
  path: null  # Override for project-specific path
  add_to_gitignore: true

# Metadata configuration  
metadata:
  include_hostname: true
  include_ip: true
  custom_fields:
    environment: "development"
    team: "engineering"
```

### settings.json Schema

Claude Code hook configuration (managed by `eyelet configure`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",  // Regex for tool names
        "hooks": [
          {
            "type": "command",
            "command": "uvx eyelet execute --log-only"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "uvx eyelet execute --log-only"
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "manual",  // or "auto"
        "hooks": [
          {
            "type": "command",
            "command": "uvx eyelet execute --log-only"
          }
        ]
      }
    ]
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EYELET_CONFIG_DIR` | Override config directory | Current directory |
| `EYELET_LOG_LEVEL` | Logging level | INFO |
| `EYELET_NO_COLOR` | Disable colored output | false |
| `EYELET_JSON_LOGS` | Force JSON log output | false |

---

## Python API

### Core Classes

#### Hook

```python
from eyelet.domain.models import Hook, HookType, Handler, HandlerType

hook = Hook(
    type=HookType.PRE_TOOL_USE,
    matcher="Bash",
    handler=Handler(
        type=HandlerType.COMMAND,
        command="uvx eyelet execute --log-only"
    ),
    description="Log Bash commands",
    enabled=True
)
```

#### HookConfiguration

```python
from eyelet.domain.models import HookConfiguration

config = HookConfiguration()
config.add_hook(hook)
config.remove_hook("hook_id")
hooks = config.get_hooks_by_type(HookType.PRE_TOOL_USE)
```

#### ConfigService

```python
from eyelet.services.config_service import ConfigService

service = ConfigService()
config = service.get_config()  # Get merged configuration
service.save_project_config(config)
```

#### HookLogger

```python
from eyelet.services.hook_logger import HookLogger

logger = HookLogger(config_service, project_dir)
log_results = logger.log_hook(input_data, timestamp)
logger.update_hook_result(hook_data, status="success", duration_ms=100)
```

### Extension Points

Custom hook handlers can be implemented by:

1. Creating a command that reads JSON from stdin
2. Processing the hook event data
3. Returning appropriate exit codes
4. Optionally outputting JSON to stdout

Example handler:
```python
#!/usr/bin/env python3
import json
import sys

# Read hook data
data = json.load(sys.stdin)

# Process based on hook type
if data["hook_event_name"] == "PreToolUse":
    if data["tool_name"] == "Bash":
        command = data["tool_input"]["command"]
        if "rm -rf" in command:
            print("Dangerous command blocked", file=sys.stderr)
            sys.exit(2)  # Block execution

sys.exit(0)  # Allow execution
```

---

## Template API

### Template JSON Schema

```json
{
  "id": "bash-validator",
  "name": "Bash Command Validator",
  "description": "Validates bash commands for safety",
  "category": "security",
  "version": "1.0.0",
  "author": "Eyelet Team",
  "tags": ["security", "bash", "validation"],
  "hooks": [
    {
      "type": "PreToolUse",
      "matcher": "Bash",
      "handler": {
        "type": "command",
        "command": "{{validator_path}}"
      },
      "description": "Validate bash commands"
    }
  ],
  "variables": {
    "validator_path": "/usr/local/bin/bash-validator"
  }
}
```

### Variable Substitution

Templates support variable substitution using `{{variable_name}}` syntax:

- Variables can be defined in the template's `variables` section
- Users can override variables during installation
- Variables are substituted in all string fields

Example:
```bash
eyelet template install bash-validator --var validator_path=/custom/path/validator
```

---

## Logging API

### Log Formats

#### JSON Log Format

Each log entry is a JSON file with this structure:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "timestamp_unix": 1704110400.0,
  "hook_type": "PreToolUse",
  "tool_name": "Bash",
  "session_id": "uuid",
  "transcript_path": "/path/to/transcript",
  "cwd": "/working/directory",
  "environment": {
    "python_version": "3.11.0",
    "platform": "darwin",
    "eyelet_version": "0.2.0",
    "env_vars": {}
  },
  "input_data": {},
  "metadata": {
    "log_file": "/path/to/log.json",
    "log_dir": "/path/to/logs",
    "project_dir": "/project"
  },
  "execution": {
    "status": "success",
    "duration_ms": 100,
    "output_data": {},
    "error_message": null
  }
}
```

#### SQLite Schema

```sql
-- Main hooks table
CREATE TABLE hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    hook_type TEXT NOT NULL,
    tool_name TEXT,
    session_id TEXT NOT NULL,
    transcript_path TEXT,
    cwd TEXT,
    status TEXT DEFAULT 'pending',
    duration_ms INTEGER,
    error_message TEXT,
    
    -- JSON columns
    input_data TEXT NOT NULL,  -- JSON
    output_data TEXT,          -- JSON
    environment TEXT,          -- JSON
    git_metadata TEXT,         -- JSON
    
    -- Metadata
    hostname TEXT,
    ip_address TEXT,
    python_version TEXT,
    platform TEXT,
    eyelet_version TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_hooks_timestamp ON hooks(timestamp);
CREATE INDEX idx_hooks_hook_type ON hooks(hook_type);
CREATE INDEX idx_hooks_tool_name ON hooks(tool_name);
CREATE INDEX idx_hooks_session_id ON hooks(session_id);
CREATE INDEX idx_hooks_status ON hooks(status);
CREATE INDEX idx_hooks_created_at ON hooks(created_at);

-- JSON extraction indexes (SQLite 3.38.0+)
CREATE INDEX idx_hooks_git_branch ON hooks(json_extract(git_metadata, '$.branch'));
```

### Query Interface

The QueryService provides programmatic access to logs:

```python
from eyelet.services.query_service import QueryService, QueryFilter
from datetime import datetime, timedelta

service = QueryService(config_service)

# Search with filters
filter = QueryFilter(
    hook_type="PreToolUse",
    tool_name="Bash",
    since=datetime.now() - timedelta(hours=1),
    status="error",
    limit=50
)
results = service.query(filter)

# Get summary statistics
stats = service.get_summary(since=datetime.now() - timedelta(days=1))

# Get recent errors
errors = service.get_recent_errors(limit=10)

# Get session timeline
timeline = service.get_session_timeline("session_id")

# Search logs for text
results = service.search_logs("search_term", limit=20)
```

---

## Error Codes and Messages

### Common Error Messages

| Error | Description | Resolution |
|-------|-------------|------------|
| `No Claude settings.json found` | Claude Code configuration missing | Run `eyelet configure install-all` |
| `Invalid JSON in settings.json` | Malformed configuration file | Validate with `eyelet validate settings` |
| `No write permission` | Cannot write to log directory | Check directory permissions |
| `Database integrity check failed` | SQLite database corrupted | Run `eyelet doctor --fix` |
| `Hook command not found` | Executable in hook command missing | Check command path |
| `Template not found` | Referenced template doesn't exist | List available with `eyelet template list` |
| `Variable required` | Template variable not provided | Supply with `--var KEY=VALUE` |

### Hook Execution Errors

| Error | Description | Resolution |
|-------|-------------|------------|
| `Failed to parse JSON input` | Invalid JSON from Claude Code | Check hook configuration |
| `Workflow not found` | Referenced workflow missing | Check workflow path |
| `Command execution failed` | Hook command returned error | Check command and logs |
| `Timeout exceeded` | Hook took too long | Optimize hook command |

### Configuration Errors

| Error | Description | Resolution |
|-------|-------------|------------|
| `Invalid hook type` | Unknown hook type in config | Use valid types: PreToolUse, PostToolUse, etc. |
| `Invalid matcher` | Bad regex or matcher value | Check matcher syntax |
| `Missing required field` | Configuration missing fields | Add required fields |
| `Schema validation failed` | Config doesn't match schema | Run `eyelet validate settings` |

---

## Examples

### Basic Hook Installation

```bash
# Install universal logging
eyelet configure install-all

# Check configuration
eyelet configure list

# Validate setup
eyelet doctor
```

### Custom Hook Configuration

```bash
# Add a custom hook
eyelet configure add

# Install from template
eyelet template install bash-validator

# Create custom template
eyelet template create
```

### Log Analysis

```bash
# View recent activity
eyelet query summary

# Search for errors
eyelet query search --errors-only --since 1h

# Analyze specific session
eyelet query session abc123...

# Search for specific content
eyelet query grep "rm -rf"
```

### Troubleshooting

```bash
# Run diagnostics
eyelet doctor --verbose

# Fix issues automatically
eyelet doctor --fix

# Validate configuration
eyelet validate settings
eyelet validate hooks
```

---

*For more examples and tutorials, see the [Quickstart Guide](QUICKSTART.md).*