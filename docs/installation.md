# Eyelet Installation Guide

Welcome aboard! This guide will help you install and configure Eyelet, the sophisticated hook orchestration system for Claude Code.

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Logging Options](#logging-options)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## System Requirements

Before installing Eyelet, ensure your system meets these requirements:

- **Python**: 3.11 or higher
- **Package Manager**: One of:
  - `uv` (recommended) - [Install uv](https://github.com/astral-sh/uv)
  - `pipx` - [Install pipx](https://pipx.pypa.io/)
  - `pip` - Comes with Python
- **Operating System**: Linux, macOS, or Windows
- **Disk Space**: ~50MB for Eyelet + space for logs
- **Optional**: Git (for enriched metadata in logs)

### Checking Requirements

```bash
# Check Python version
python --version  # Should show 3.11 or higher

# Check if uv is installed (recommended)
uv --version

# Check if pipx is installed (alternative)
pipx --version

# Check if git is installed (optional but recommended)
git --version
```

## Installation Methods

### Method 1: Using uvx (Recommended)

The fastest way to use Eyelet without installation:

```bash
# Run Eyelet directly
uvx eyelet --version

# Or install permanently with uv
uv tool install eyelet
```

### Method 2: Using pipx

Install Eyelet in an isolated environment:

```bash
# Install Eyelet
pipx install eyelet

# Verify installation
eyelet --version
```

### Method 3: Using pip

Install in your current Python environment:

```bash
# Install from PyPI
pip install eyelet

# Verify installation
eyelet --version
```

### Method 4: From Source

For development or latest features:

```bash
# Clone the repository
git clone https://github.com/bdmorin/eyelet.git
cd eyelet

# Install with uv (recommended)
uv pip install -e .

# Or install with pip
pip install -e .

# Verify installation
eyelet --version
```

## Quick Start

Get Eyelet up and running in minutes:

### 1. Install Universal Logging (Recommended!)

This single command sets up comprehensive logging for ALL Claude Code hooks:

```bash
# Install logging for all hooks - one command does it all!
uvx eyelet configure install-all

# What this does:
# ✅ Configures PreToolUse hooks for all tools
# ✅ Configures PostToolUse hooks for all tools
# ✅ Sets up UserPromptSubmit, Stop, and PreCompact hooks
# ✅ Creates ./eyelet-hooks/ directory structure
# ✅ Updates your Claude settings.json
```

### 2. Enable SQLite Logging (Optional but Powerful)

For better performance and advanced querying:

```bash
# Enable SQLite database logging
uvx eyelet configure logging --format sqlite

# Or use both JSON and SQLite
uvx eyelet configure logging --format json,sqlite
```

### 3. Check Installation Health

Verify everything is configured correctly:

```bash
# Run comprehensive health check
uvx eyelet doctor

# Run with auto-fix for common issues
uvx eyelet doctor --fix

# Show detailed diagnostics
uvx eyelet doctor --verbose
```

### 4. Validate Claude Settings

Ensure your Claude configuration is valid:

```bash
# Validate settings files
uvx eyelet validate settings

# Validate a specific file
uvx eyelet validate settings ~/.claude/settings.json
```

## Configuration

Eyelet uses a layered configuration system with two levels:

### Configuration Files

1. **Global Configuration**: `~/.claude/eyelet.yaml`
   - Applies to all projects
   - User-wide settings
   - Default logging preferences

2. **Project Configuration**: `./eyelet.yaml`
   - Project-specific settings
   - Overrides global settings
   - Committed to version control

### Configuration Structure

```yaml
# Example eyelet.yaml
logging:
  format: sqlite          # json, sqlite, or both
  scope: project          # global, project, or both
  enabled: true           # Enable/disable logging
  add_to_gitignore: true  # Auto-add log dirs to .gitignore

hooks:
  # Hook configurations are managed via CLI
  # Use 'eyelet configure' commands
```

### Managing Configuration

```bash
# Show current logging configuration
uvx eyelet configure logging

# Set logging format
uvx eyelet configure logging --format sqlite

# Set logging scope
uvx eyelet configure logging --scope both

# Configure global settings
uvx eyelet configure logging --format json --global

# Disable logging temporarily
uvx eyelet configure logging --disabled
```

## Logging Options

Eyelet supports flexible logging configurations:

### Logging Formats

1. **JSON Files** (Default)
   - Human-readable format
   - One file per hook execution
   - Easy to grep and parse
   - Good for debugging

2. **SQLite Database**
   - High-performance queries
   - Full-text search
   - Advanced analytics
   - Compact storage

3. **Both Formats**
   - Best of both worlds
   - JSON for debugging
   - SQLite for analysis

### Setting Logging Format

```bash
# Use JSON files only
uvx eyelet configure logging --format json

# Use SQLite database only
uvx eyelet configure logging --format sqlite

# Use both formats
uvx eyelet configure logging --format json,sqlite
```

### Logging Scopes

1. **Project** (Default)
   - Logs stored in `./eyelet-hooks/`
   - Project-specific data
   - Easy to share with team

2. **Global**
   - Logs stored in `~/.claude/eyelet-logs/`
   - Cross-project analytics
   - Personal usage patterns

3. **Both**
   - Logs to both locations
   - Maximum visibility
   - Useful for consultants

### Setting Logging Scope

```bash
# Log to project directory only
uvx eyelet configure logging --scope project

# Log to global directory only
uvx eyelet configure logging --scope global

# Log to both locations
uvx eyelet configure logging --scope both
```

## Verification

After installation, verify everything is working:

### 1. Version Check

```bash
uvx eyelet --version
# Should show: eyelet version X.X.X
```

### 2. Doctor Check

```bash
uvx eyelet doctor
# Should show all green checkmarks
```

### 3. Configuration Check

```bash
# List configured hooks
uvx eyelet configure list

# Show logging settings
uvx eyelet configure logging
```

### 4. Test Hook Execution

```bash
# Manually test a hook
echo '{"tool": "Bash", "arguments": {"command": "echo test"}}' | uvx eyelet execute --log-only

# Check if log was created
uvx eyelet logs --tail 1
```

## Troubleshooting

### Common Issues and Solutions

#### Python Version Error

**Problem**: `Python 3.11+ required`

**Solution**:
```bash
# Check your Python version
python --version

# Install Python 3.11+ using your system package manager
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
# Or use pyenv/mise for version management
```

#### Permission Denied

**Problem**: `Permission denied` when creating log directories

**Solution**:
```bash
# Fix with doctor command
uvx eyelet doctor --fix

# Or manually create directories
mkdir -p ./eyelet-hooks
chmod 755 ./eyelet-hooks
```

#### Claude Settings Not Found

**Problem**: `No Claude settings.json found`

**Solution**:
```bash
# Create Claude settings directory
mkdir -p ~/.claude

# Run install-all to create initial settings
uvx eyelet configure install-all
```

#### SQLite Errors

**Problem**: SQLite-related errors

**Solution**:
```bash
# Check SQLite version
uvx eyelet doctor --verbose

# If JSON1 extension missing, update SQLite
# Or use JSON logging format instead:
uvx eyelet configure logging --format json
```

#### Hooks Not Firing

**Problem**: Hooks configured but not executing

**Solution**:
```bash
# Verify hook configuration
uvx eyelet configure list

# Check Claude is using correct settings file
uvx eyelet doctor --verbose

# Ensure hooks are enabled
uvx eyelet configure enable <hook-id>
```

### Getting Help

If you encounter issues not covered here:

1. Run diagnostics: `uvx eyelet doctor --verbose`
2. Check logs: `uvx eyelet logs --tail 50`
3. Visit [GitHub Issues](https://github.com/bdmorin/eyelet/issues)
4. Review [documentation](https://github.com/bdmorin/eyelet/tree/main/docs)

## Uninstallation

### Remove Eyelet Package

Depending on how you installed:

```bash
# If installed with uv tool
uv tool uninstall eyelet

# If installed with pipx
pipx uninstall eyelet

# If installed with pip
pip uninstall eyelet
```

### Remove Configuration and Logs

```bash
# Remove project configuration
rm -f eyelet.yaml
rm -rf ./eyelet-hooks/

# Remove global configuration (optional)
rm -f ~/.claude/eyelet.yaml
rm -rf ~/.claude/eyelet-logs/

# Remove from Claude settings
# Edit ~/.claude/settings.json and remove eyelet hooks
```

### Clean Git Ignore

If you added log directories to `.gitignore`:

```bash
# Remove these lines from .gitignore:
# .eyelet-logs/
# .eyelet-logging/
# eyelet-hooks/
```

## Next Steps

Now that Eyelet is installed:

1. **Explore Commands**: Run `uvx eyelet --help` to see all available commands
2. **Query Your Data**: Try `uvx eyelet query summary` after some usage
3. **Create Workflows**: Check out the [workflow documentation](workflows.md)
4. **Browse Templates**: See available templates with `uvx eyelet template list`

Welcome to the Eyelet community! ⚓

---

*"Thread through the eyelet!" - Happy hook orchestration!*