# 🔗 Eyelet - Hook Orchestration for AI Agents

> "Thread through the eyelet!" - A sophisticated hook management system for AI agent workflows

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/eyelet.svg)](https://badge.fury.io/py/eyelet)
[![uv](https://img.shields.io/badge/uv-latest-green)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/bdmorin/eyelet/actions/workflows/ci.yml/badge.svg)](https://github.com/bdmorin/eyelet/actions/workflows/ci.yml)

Eyelet provides comprehensive management, templating, and execution handling for AI agent hooks. Like an eyelet that securely connects hooks to fabric, Eyelet connects and orchestrates your AI agent's behavior through a reliable workflow system.

## 🚀 Quick Start

```bash
# Install with uvx (recommended)
uvx eyelet

# Install universal logging for ALL hooks (recommended!)
uvx eyelet configure install-all

# Thread through the eyelet with the TUI
uvx eyelet

# Configure hooks for your project
uvx eyelet configure --scope project

# Deploy a template
uvx eyelet template install observability
```

## 🎯 Universal Hook Handler

Eyelet includes a powerful universal hook handler that logs EVERY Claude Code hook to a structured directory:

```bash
# Install logging for all hooks with one command
uvx eyelet configure install-all

# Your hooks will be logged to:
./eyelet-hooks/
├── PreToolUse/
│   └── Bash/2025-07-28/
│       └── 20250728_133300_236408_PreToolUse_Bash.json
├── PostToolUse/
│   └── Read/2025-07-28/
├── UserPromptSubmit/2025-07-28/
├── Stop/2025-07-28/
└── PreCompact/manual/2025-07-28/
```

Each log contains:
- Complete input data from Claude Code
- Environment variables and context
- Timestamps (ISO and Unix)
- Session information
- Tool inputs/outputs
- Python version and platform details

## 🎯 Features

- **Dynamic Hook Discovery** - Automatically detects new tools and generates all valid hook combinations
- **Beautiful TUI** - Navigate with a Textual-powered interface for reliable connections  
- **Template System** - Deploy pre-configured hook patterns with a single command
- **Workflow Engine** - Chain complex behaviors with conditional logic
- **Comprehensive Logging** - Track every hook execution in SQLite or filesystem
- **AI Integration** - Native Claude Code SDK support for intelligent workflows
- **Real-time Monitoring** - Watch hook executions as they happen

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Hook Types & Matchers](docs/hooks.md)
- [Creating Workflows](docs/workflows.md)
- [Template Library](docs/templates.md)
- [API Reference](docs/api.md)

## 🛠️ Commands

```bash
# Core Operations
uvx eyelet configure    # Configure hooks
uvx eyelet execute      # Run as hook endpoint
uvx eyelet logs         # View execution logs

# Discovery & Generation  
uvx eyelet discover     # Find available hooks
uvx eyelet generate     # Create hook combinations
uvx eyelet update       # Check for updates

# Templates & Workflows
uvx eyelet template list      # Browse available templates
uvx eyelet template install   # Deploy a template
uvx eyelet workflow create    # Build custom workflows
```

## 🎨 Example Hook Configuration

```json
{
  "hooks": [{
    "type": "PreToolUse",
    "matcher": "Bash",
    "handler": {
      "type": "command", 
      "command": "uvx eyelet execute --workflow bash-validator"
    }
  }]
}
```

## 🔍 JSON Validation & Linting

Eyelet provides built-in validation for Claude settings files and VS Code integration:

```bash
# Validate your Claude settings
uvx eyelet validate settings

# Validate a specific file
uvx eyelet validate settings ~/.claude/settings.json
```

### VS Code Integration

The project includes a JSON schema for Claude settings files. VS Code users get:
- ✅ IntelliSense/autocomplete for hook configurations
- ✅ Real-time error detection
- ✅ Hover documentation

See [docs/vscode-json-linting.md](docs/vscode-json-linting.md) for setup instructions.

## 🔗 Connection Philosophy

Eyelet embraces hardware connection terminology for reliable, secure attachment:

- **"Thread through the eyelet!"** - Launch the TUI
- **"Secure the connection!"** - Deploy templates  
- **"Check the connection log"** - View logs
- **"Scan for connection points"** - Discover new hooks
- **"Hold fast!"** - Maintain current configuration

## 🧪 Testing

Eyelet includes comprehensive testing tools to ensure your hooks are working correctly:

### Testing Hook Integration

```bash
# Run the interactive hook test
mise run test-hooks

# This will generate a unique test ID and guide you through testing all tools
# After running the test commands, verify with:
mise run test-hooks-verify zebra-1234-flamingo-5678

# View hook statistics
mise run hook-stats

# Generate a coverage report
mise run hook-coverage

# Clean old logs (older than 7 days)
mise run hook-clean
```

### Development Testing

```bash
# Run all tests
mise run test

# Run linting
mise run lint

# Run type checking
mise run typecheck

# Run all CI checks
mise run ci
```

### Manual Hook Testing

The `test_all_hooks.py` script provides comprehensive hook testing:
- Generates unique test identifiers for tracking
- Tests all Claude Code tools (Bash, Read, Write, Edit, etc.)
- Verifies hook logs contain expected data
- Provides coverage reports

## 🤝 Contributing

We welcome contributions! Please open issues and pull requests on GitHub.

## 📚 Documentation

- **[Quickstart Guide](docs/QUICKSTART.md)** - Get up and running quickly
- **[Design Documents](docs/design/)** - Architecture and design decisions
- **[Setup Guides](docs/setup/)** - GitHub Actions and deployment setup

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with love for the AI development community. Special thanks to the Anthropic team for Claude Code and its powerful hook system.

---

*"The strongest connections are forged under pressure." - Connect with Eyelet and explore the possibilities of AI agent orchestration.*