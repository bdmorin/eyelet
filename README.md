# 🔗 Eyelet - Hook Orchestration for AI Agents

> "Thread through the eyelet!" - A sophisticated hook management system for AI agent workflows

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/eyelet.svg)](https://badge.fury.io/py/eyelet)
[![uv](https://img.shields.io/badge/uv-latest-green)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/bdmorin/eyelet/actions/workflows/ci.yml/badge.svg)](https://github.com/bdmorin/eyelet/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/status-alpha-yellow)](https://github.com/bdmorin/eyelet)

## 🎉 New in v0.3.4: Auto-update Support & Critical Fixes!

### v0.3.4 Updates
- **Auto-update support**: `--autoupdate` flag for install-all command
- **Version detection**: Doctor command warns about unpinned versions
- **Critical fix**: Execute command now supports both hook_type and hook_event_name
- **Enhanced doctor**: Clear guidance on enabling auto-updates

### v0.3.3 Updates (Hotfix)
- Fixed missing TUI module in PyPI package
- Added .tcss file to package data

### v0.3.2 Updates
- **Recall Feature**: Search Claude Code conversation history with `eyelet recall`
- **TUI Framework**: Complete Textual-based UI (experimental)
- **Test Improvements**: Better test coverage and pytest-asyncio support

### v0.3.0 Features
**SQLite database logging support!** Choose between JSON files, SQLite database, or both:

```bash
# Enable SQLite logging
uvx eyelet configure logging --format sqlite

# Use both JSON and SQLite
uvx eyelet configure logging --format json,sqlite

# Query your hook data
uvx eyelet query search --text "error"
uvx eyelet query summary --last 24h
```

## 📦 About

Eyelet provides comprehensive management, templating, and execution handling for AI agent hooks. Like an eyelet that securely connects hooks to fabric, Eyelet connects and orchestrates your AI agent's behavior through a reliable workflow system.

## ✨ Features

- 🪝 **Universal Hook Support** - Captures all Claude Code hook types ✅
- 💾 **Flexible Logging** - JSON files, SQLite database, or both ✅
- 🔍 **Powerful Queries** - Search, filter, and analyze your hook data ✅
- 🏥 **Health Monitoring** - `eyelet doctor` checks your configuration ✅
- 🚀 **Zero Config** - `eyelet configure install-all` sets up everything ✅
- 📊 **Rich Analytics** - Session summaries, error analysis, and more ✅
- 🔧 **Git Integration** - Automatic Git metadata enrichment ✅
- ⚡ **High Performance** - SQLite with WAL mode for concurrent access ✅

## 🚀 Quick Start

```bash
# Install universal logging for ALL hooks with auto-updates
uvx eyelet configure install-all --autoupdate

# Or install without auto-updates (manual updates required)
uvx eyelet configure install-all

# Enable SQLite logging for better performance
uvx eyelet configure logging --format sqlite

# Check your configuration health (detects unpinned versions)
uvx eyelet doctor

# Query your hook data
uvx eyelet query summary          # Session overview
uvx eyelet query search --help    # Search options
uvx eyelet query errors           # Debug issues
```

### ⚠️ Important: Version Updates

By default, `uvx eyelet` caches the package and won't auto-update. You have three options:

1. **Enable auto-updates** (recommended):
   ```bash
   uvx eyelet configure install-all --autoupdate
   ```
   This uses `uvx eyelet@latest` which always fetches the latest version.

2. **Manual update** when needed:
   ```bash
   uvx --reinstall eyelet@latest execute --log-only
   ```

3. **Use pipx** for global installation:
   ```bash
   pipx install eyelet
   pipx upgrade eyelet  # When updates are available
   ```

Run `eyelet doctor` to check if your hooks are configured for auto-updates.

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

- **Dynamic Hook Discovery** - Automatically detects new tools and generates all valid hook combinations ✅
- **Beautiful TUI** - Navigate with a Textual-powered interface for reliable connections ✅ 
- **Template System** - Deploy pre-configured hook patterns with a single command ✅
- **Workflow Engine** - Chain complex behaviors with conditional logic ❌ (Not implemented - raises NotImplementedError)
- **Comprehensive Logging** - Track every hook execution in SQLite or filesystem ✅
- **AI Integration** - Native Claude Code SDK support for intelligent workflows ✅
- **Real-time Monitoring** - Watch hook executions as they happen ✅ (via `eyelet logs --follow`)

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Hook Types & Matchers](docs/hooks.md)
- [Creating Workflows](docs/workflows.md)
- [Template Library](docs/templates.md)
- [API Reference](docs/api.md)

## 🛠️ Commands

```bash
# Core Operations
uvx eyelet configure         # Configure hooks ✅
uvx eyelet configure logging # Manage logging settings (JSON/SQLite) ✅
uvx eyelet execute          # Run as hook endpoint ✅
uvx eyelet logs             # View JSON execution logs ✅
uvx eyelet doctor           # Health check and diagnostics ✅
uvx eyelet recall           # Search Claude Code conversations (NEW!) ✅

# Query & Analytics (SQLite)
uvx eyelet query search     # Full-text search with filters ✅
uvx eyelet query summary    # Session and hook statistics ✅
uvx eyelet query errors     # Error analysis and debugging ✅
uvx eyelet query session    # View specific session logs ✅
uvx eyelet query grep       # Pattern matching across logs ✅

# Discovery & Templates  
uvx eyelet discover         # Find available hooks ✅
uvx eyelet template list    # Browse templates ✅
uvx eyelet template install # Deploy a template ✅
```

## 💾 SQLite Logging

Eyelet's SQLite logging provides powerful analytics and querying capabilities:

```bash
# Enable SQLite logging
uvx eyelet configure logging --format sqlite

# Search for specific patterns
uvx eyelet query search --text "error" --tool Bash --last 1h

# Get session summary
uvx eyelet query summary --format json

# Analyze errors
uvx eyelet query errors --last 24h

# Export specific session
uvx eyelet query session <session-id> --format json > session.json
```

### Why SQLite?
- ⚡ **Fast queries** across millions of hooks
- 🔍 **Full-text search** with advanced filters
- 📊 **Analytics** without external dependencies
- 🔄 **Concurrent access** with WAL mode
- 💾 **Compact storage** compared to JSON files

## 🎨 Example Hook Configuration

```json
{
  "hooks": [{
    "type": "PreToolUse",
    "matcher": "Bash",
    "handler": {
      "type": "command", 
      "command": "uvx eyelet execute --log-only"
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
- ✅ IntelliSense/autocomplete for hook configurations ⚠️ (Schema exists but no .vscode/settings.json in project)
- ✅ Real-time error detection ⚠️ (Schema exists but VS Code config not set up)
- ✅ Hover documentation ⚠️ (Schema exists but VS Code config not set up)

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