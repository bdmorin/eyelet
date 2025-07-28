# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research and testing repository for Claude Code hooks functionality. It contains documentation and utilities for understanding and experimenting with Claude Code's hook system, which enables observability and control over Claude Code agent behavior.

## Repository Structure

The repository contains three main components:

- **claude-code-hooks.md**: Comprehensive technical documentation about IndyDevDan's multi-agent observability system
- **hook-logger.sh**: Bash script utility for logging Claude Code hook execution data  
- **hook-execution.log**: Log file containing captured hook execution details

## Key Components

### Hook Logger Script (`hook-logger.sh`)

This executable bash script is designed to be used as a Claude Code hook to capture and log all available execution context. When executed as a hook, it logs:

- Command line arguments passed to the hook
- Environment variables available during execution
- STDIN data (including JSON parsing if available)
- Working directory and process information
- Timestamp of execution

The script always exits with code 0 to avoid blocking Claude Code operations, making it safe for experimentation.

### Documentation (`claude-code-hooks.md`)

Contains detailed technical analysis of a sophisticated multi-agent observability system including:

- Architecture patterns for monitoring Claude Code agents
- Hook implementation strategies across all seven lifecycle events
- Real-time visualization and WebSocket streaming approaches
- Cost-efficient AI summarization using Anthropic's Haiku model
- Performance optimization strategies for multi-agent environments

## Usage

### Running the Hook Logger

The hook-logger.sh script is designed to be configured as a Claude Code hook in your `.claude/settings.json` file. Example configuration:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": ".*",
      "hooks": [{
        "type": "command",
        "command": "/Users/bdmorin/src/claude-hooks/hook-logger.sh"
      }]
    }]
  }
}
```

### Viewing Execution Data

Hook execution data is logged to `hook-execution.log` with timestamps and detailed environment information. This can be useful for:

- Understanding what data is available to hooks
- Debugging hook execution issues
- Analyzing Claude Code agent behavior patterns

## Development Notes

- The hook-logger.sh script requires bash and optionally uses `jq` for JSON parsing
- The script is designed to be non-blocking and safe for production use
- Log files can grow large with frequent hook executions - consider log rotation for long-term use
- Environment variables may contain sensitive information - review logs before sharing

## Hook System Context

This repository serves as a reference for understanding Claude Code's hook system capabilities, which enable:

- **PreToolUse/PostToolUse**: Tool execution monitoring and control
- **Notification**: User interaction tracking
- **UserPromptSubmit**: Prompt validation and context injection
- **Stop/SubagentStop**: Session and subtask completion handling
- **PreCompact**: Context management monitoring

The documentation provides insights into building sophisticated observability systems on top of these hook primitives.