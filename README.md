# ⚓ Rigging - Hook Orchestration for AI Agents

> "All hands to the rigging!" - A sophisticated hook management system for AI agent workflows

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/rigging-cli.svg)](https://badge.fury.io/py/rigging-cli)
[![uv](https://img.shields.io/badge/uv-latest-green)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/bdmorin/rigging-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/bdmorin/rigging-cli/actions/workflows/ci.yml)

Rigging provides comprehensive management, templating, and execution handling for AI agent hooks. Like a ship's rigging that controls the sails and direction, Rigging controls and orchestrates your AI agent's behavior through a powerful workflow system.

## 🚀 Quick Start

> **Note**: All commands use `uvx --from rigging-cli rigging` because the package is published as `rigging-cli` on PyPI.

```bash
# Install with uvx (recommended)
uvx --from rigging-cli rigging

# Install universal logging for ALL hooks (recommended!)
uvx --from rigging-cli rigging configure install-all

# Set sail with the TUI
uvx --from rigging-cli rigging

# Configure hooks for your project
uvx --from rigging-cli rigging configure --scope project

# Deploy a template
uvx --from rigging-cli rigging template install observability
```

## 🎯 Universal Hook Handler

Rigging includes a powerful universal hook handler that logs EVERY Claude Code hook to a structured directory:

```bash
# Install logging for all hooks with one command
uvx --from rigging-cli rigging configure install-all

# Your hooks will be logged to:
./hms-hooks/
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
- **Beautiful TUI** - Navigate with a Textual-powered interface worthy of a ship's bridge  
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
uvx --from rigging-cli rigging configure    # Configure hooks
uvx --from rigging-cli rigging execute      # Run as hook endpoint
uvx --from rigging-cli rigging logs         # View execution logs

# Discovery & Generation  
uvx --from rigging-cli rigging discover     # Find available hooks
uvx --from rigging-cli rigging generate     # Create hook combinations
uvx --from rigging-cli rigging update       # Check for updates

# Templates & Workflows
uvx --from rigging-cli rigging template list      # Browse available templates
uvx --from rigging-cli rigging template install   # Deploy a template
uvx --from rigging-cli rigging workflow create    # Build custom workflows
```

## 🎨 Example Hook Configuration

```json
{
  "hooks": [{
    "type": "PreToolUse",
    "matcher": "Bash",
    "handler": {
      "type": "command", 
      "command": "uvx --from rigging-cli rigging execute --workflow bash-validator"
    }
  }]
}
```

## 🔍 JSON Validation & Linting

Rigging provides built-in validation for Claude settings files and VS Code integration:

```bash
# Validate your Claude settings
uvx --from rigging-cli rigging validate settings

# Validate a specific file
uvx --from rigging-cli rigging validate settings ~/.claude/settings.json
```

### VS Code Integration

The project includes a JSON schema for Claude settings files. VS Code users get:
- ✅ IntelliSense/autocomplete for hook configurations
- ✅ Real-time error detection
- ✅ Hover documentation

See [docs/vscode-json-linting.md](docs/vscode-json-linting.md) for setup instructions.

## 🚢 Naval Tradition

Rigging embraces naval terminology in honor of staying organized and shipshape:

- **"All hands to the rigging!"** - Launch the TUI
- **"Run out the guns!"** - Deploy templates  
- **"Check the ship's log"** - View logs
- **"Scan the horizon"** - Discover new hooks
- **"Steady as she goes"** - Maintain current configuration

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

*"A ship is safe in harbor, but that's not what ships are for." - Set sail with Rigging and explore the possibilities of AI agent orchestration.*