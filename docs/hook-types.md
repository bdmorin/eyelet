# Hook Types & Matchers Documentation

This comprehensive guide covers all hook types available in Claude Code, their matchers, handler types, and configuration patterns for Eyelet.

## Overview

Claude Code's hook system allows you to intercept and respond to various events during AI agent execution. Eyelet provides a sophisticated orchestration layer for managing these hooks, supporting everything from simple logging to complex multi-step workflows.

### Hook Categories

1. **Tool Hooks**: Intercept before/after tool execution (PreToolUse, PostToolUse)
2. **Lifecycle Hooks**: Monitor agent lifecycle events (Stop, SubagentStop)
3. **Interaction Hooks**: Track user interactions (UserPromptSubmit, Notification)
4. **System Hooks**: Handle system events (PreCompact)

## Hook Types Reference

### PreToolUse

Triggered before a tool is executed, allowing validation, modification, or cancellation of tool invocations.

**Matcher Required**: Yes (tool name pattern)  
**Common Use Cases**:
- Command validation and sandboxing
- Input parameter verification
- Access control and permissions
- Audit logging

**Example Configuration**:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet validate-bash"
          }
        ]
      }
    ]
  }
}
```

### PostToolUse

Triggered after a tool completes execution, providing access to results and output.

**Matcher Required**: Yes (tool name pattern)  
**Common Use Cases**:
- Result processing and caching
- Output validation and filtering
- Performance monitoring
- Error tracking

**Example Configuration**:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet log-result"
          }
        ]
      }
    ]
  }
}
```

### UserPromptSubmit

Triggered when a user submits a prompt, before Claude processes it.

**Matcher Required**: No  
**Common Use Cases**:
- Context injection
- Prompt enhancement
- Security filtering
- Usage tracking

**Example Configuration**:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "eyelet enhance-prompt"
          }
        ]
      }
    ]
  }
}
```

### Notification

Triggered for UI notifications and system events.

**Matcher Required**: No  
**Common Use Cases**:
- User alerts
- Status updates
- Event logging
- External notifications

**Example Configuration**:
```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "eyelet notify"
          }
        ]
      }
    ]
  }
}
```

### Stop

Triggered when the main Claude agent completes its session.

**Matcher Required**: No  
**Common Use Cases**:
- Session cleanup
- Final reporting
- Resource cleanup
- State persistence

**Example Configuration**:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "eyelet cleanup-session"
          }
        ]
      }
    ]
  }
}
```

### SubagentStop

Triggered when a subagent (Task tool) completes its work.

**Matcher Required**: No  
**Common Use Cases**:
- Task result processing
- Subagent performance tracking
- Error aggregation
- Workflow continuation

**Example Configuration**:
```json
{
  "hooks": {
    "SubagentStop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "eyelet process-subagent"
          }
        ]
      }
    ]
  }
}
```

### PreCompact

Triggered before Claude performs context compaction to manage memory.

**Matcher Required**: Yes ("manual" or "auto")  
**Common Use Cases**:
- Context preservation
- State backup
- Memory optimization
- Compaction analytics

**Example Configuration**:
```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet backup-context"
          }
        ]
      },
      {
        "matcher": "manual",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet manual-compact"
          }
        ]
      }
    ]
  }
}
```

## Tool Matchers

Tool matchers are regex patterns used with PreToolUse and PostToolUse hooks to target specific tools.

### Available Tools

| Tool | Description | Common Patterns |
|------|-------------|-----------------|
| `Task` | Subagent execution | `Task`, `^Task$` |
| `Bash` | Shell command execution | `Bash`, `^Bash$` |
| `Glob` | File pattern matching | `Glob`, `^Glob$` |
| `Grep` | Text search in files | `Grep`, `^Grep$` |
| `Read` | File reading | `Read`, `^Read$` |
| `Edit` | Single file editing | `Edit`, `^Edit$` |
| `MultiEdit` | Multiple file editing | `MultiEdit`, `^MultiEdit$` |
| `Write` | File writing | `Write`, `^Write$` |
| `WebFetch` | Web content fetching | `WebFetch`, `^WebFetch$` |
| `WebSearch` | Web searching | `WebSearch`, `^WebSearch$` |

### Matcher Patterns

#### Wildcard Pattern
Match all tools:
```json
{
  "matcher": ".*"
}
```

#### Specific Tool
Match exact tool name:
```json
{
  "matcher": "Bash"
}
```

#### Multiple Tools
Match any of several tools:
```json
{
  "matcher": "^(Bash|Edit|Write)$"
}
```

#### Tool Groups
Match tools by category:
```json
{
  "matcher": "^(Read|Write|Edit|MultiEdit)$"  // File operations
}
```

```json
{
  "matcher": "^Web.*"  // Web operations
}
```

#### Advanced Patterns
Complex regex for specific scenarios:
```json
{
  "matcher": "^(?!Task).*"  // All tools except Task
}
```

## Handler Types

Eyelet supports three types of hook handlers:

### command

Executes an external command with hook data passed via stdin.

**Structure**:
```json
{
  "type": "command",
  "command": "program arguments"
}
```

**Example**:
```json
{
  "type": "command",
  "command": "python /path/to/validator.py --strict"
}
```

### workflow

Executes a predefined Eyelet workflow (future feature).

**Structure**:
```json
{
  "type": "workflow",
  "workflow": "workflow-name"
}
```

**Example**:
```json
{
  "type": "workflow",
  "workflow": "security-scan"
}
```

### script

Executes inline script code (future feature).

**Structure**:
```json
{
  "type": "script",
  "language": "python",
  "script": "# inline code here"
}
```

## Event Data Structure

All hooks receive a JSON payload via stdin containing:

### Common Fields
```json
{
  "hook_type": "PreToolUse",
  "timestamp": "2025-07-28T10:30:00Z",
  "session_id": "session-123",
  "transcript_path": "/path/to/transcript.md",
  "cwd": "/current/working/directory"
}
```

### Tool Hook Fields (Pre/PostToolUse)
```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "ls -la",
    "description": "List directory contents"
  },
  "tool_output": {  // PostToolUse only
    "result": "...",
    "exit_code": 0
  }
}
```

### UserPromptSubmit Fields
```json
{
  "prompt": "User's input text",
  "context": {
    "previous_messages": [...],
    "session_data": {...}
  }
}
```

### PreCompact Fields
```json
{
  "compaction_type": "auto",  // or "manual"
  "context_size": 128000,
  "threshold": 100000
}
```

## Configuration Formats

Eyelet supports both the new object format and legacy array format for hooks.

### New Object Format (Recommended)
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet validate"
          }
        ]
      }
    ]
  }
}
```

### Legacy Array Format
```json
{
  "hooks": [
    {
      "type": "PreToolUse",
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "eyelet validate"
        }
      ]
    }
  ]
}
```

## Best Practices

### 1. Matcher Specificity
Start with specific matchers and broaden only when needed:
```json
// Good: Specific tool targeting
{ "matcher": "Bash" }

// Use wildcard only when you need all tools
{ "matcher": ".*" }
```

### 2. Handler Performance
- Keep handlers fast and non-blocking
- Use `--log-only` flag for logging scenarios
- Implement timeouts for long-running operations

### 3. Error Handling
- Always return appropriate exit codes
- Log errors to stderr
- Don't block Claude's execution on non-critical failures

### 4. Security Considerations
- Validate all inputs in PreToolUse hooks
- Never execute untrusted code
- Implement proper sandboxing for Bash commands
- Use access control lists for sensitive operations

### 5. Logging Strategy
- Use structured logging (JSON)
- Include correlation IDs
- Implement log rotation
- Consider privacy implications

## Common Use Cases

### 1. Command Sandboxing
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet sandbox-check --policy strict"
          }
        ]
      }
    ]
  }
}
```

### 2. Comprehensive Logging
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet execute --log-only"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet execute --log-only"
          }
        ]
      }
    ]
  }
}
```

### 3. File Operation Monitoring
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^(Read|Write|Edit|MultiEdit)$",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet file-monitor --track"
          }
        ]
      }
    ]
  }
}
```

### 4. Web Request Filtering
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "^Web.*",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet web-filter --allowlist /etc/eyelet/allowed-domains.txt"
          }
        ]
      }
    ]
  }
}
```

### 5. Context Preservation
```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "eyelet context-backup --incremental"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "eyelet context-save --final"
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

### Hooks Not Firing
1. Verify hook configuration: `eyelet configure list`
2. Check matcher patterns match tool names exactly
3. Ensure handler commands are in PATH
4. Review Claude Code logs for errors

### Performance Issues
1. Profile handler execution time
2. Use async handlers for long operations
3. Implement caching where appropriate
4. Consider using `--log-only` for non-critical hooks

### Debugging Tips
1. Enable debug logging: `EYELET_DEBUG=1`
2. Test matchers: `eyelet test-matcher "pattern" "toolname"`
3. Validate configuration: `eyelet configure validate`
4. Use dry-run mode: `eyelet configure add --dry-run`

## Future Enhancements

Planned features for hook system:
- Conditional matchers based on tool input
- Chained hook workflows
- Hook priority and ordering
- Async hook execution
- Hook result caching
- Dynamic hook loading
- Hook marketplace integration