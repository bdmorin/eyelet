# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Eyelet is a sophisticated Python-based hook orchestration system for Claude Code. It provides comprehensive management, templating, and execution handling for AI agent hooks. Like an eyelet that connects and secures, Eyelet connects and orchestrates your AI agent's behavior through hooks.

## Repository Structure

Clean, organized structure to avoid technical debt:

```
├── README.md              # Main user documentation
├── CHANGELOG.md           # Version history (MUST update for releases)
├── CLAUDE.md             # This file - AI development guidance
├── LICENSE               # MIT license
├── pyproject.toml        # Python project configuration
├── uv.lock              # Dependency lockfile
├── MANIFEST.in          # Package manifest
├── src/eyelet/          # Main Python package
├── tests/               # Test suite
├── schemas/             # JSON schemas
├── docs/                # Documentation
│   ├── QUICKSTART.md    # User quickstart guide
│   ├── design/          # Architecture and design docs
│   └── setup/           # GitHub/PyPI setup guides
└── archive/             # Historical materials

## Technology Stack

- **Language**: Python 3.11+
- **Distribution**: uvx/pipx (PyPI package: eyelet)
- **TUI**: Textual (not Bubbletea)
- **CLI**: Click
- **Architecture**: Vertical slice with separation of concerns
- **Philosophy**: "Retreat Only With Human Approval"

## Development Guidelines

### Hook System Implementation

Eyelet will support all seven Claude Code hook types:
- PreToolUse/PostToolUse: Tool execution monitoring and control
- Notification: User interaction tracking
- UserPromptSubmit: Prompt validation and context injection
- Stop/SubagentStop: Session and subtask completion handling
- PreCompact: Context management monitoring

### Eyelet Theming

The project uses eyelet/hook terminology:
- "Thread through the eyelet!" - Launch the TUI (connecting hooks through the eyelet)
- "Deploy templates" - Install hook templates
- "View logs" - Check hook execution history
- "Discover hooks" - Find available hooks and tools
- "Maintain configuration" - Keep current hook setup

## Current Status

The repository is in transition from Go concept to Python implementation. Historical research and utilities are preserved in the archive directory for reference.

## Responsibilities

- You are 100% responsible for this directory, its management, and how it's implemented. The user will guide you, however it's your responsibility to maintain it to the high standards you would expect.
- When implementing Eyelet, follow the TECHNOLOGY_GUIDE.md philosophy: troubleshoot and solve problems rather than abandoning approaches.
- Maintain consistency with the eyelet/hook theme and Python technology choices outlined in our documentation.

## Documentation Guidelines

- You must keep documentation up to date in this repository. If we dont' update documentation future context will get confused.

## Design Considerations

- It's really important to me that this CLI autocomplete options, even stuff the user doesn't know.

## ⚠️ Technical Debt Prevention

### Critical Files Requiring Regular Attention

#### 1. Version Management & Releases
- **pyproject.toml**: Version number, dependencies, package metadata
- **CHANGELOG.md**: MUST be updated before every release with user-facing changes
- **README.md**: Badge URLs, installation commands, examples must stay current
- **src/eyelet/__init__.py**: Version string must match pyproject.toml

#### 2. Documentation Synchronization
- **README.md** ↔ **docs/QUICKSTART.md**: Examples and commands must match
- **pyproject.toml** dependencies ↔ **docs/setup/** guides: Setup instructions must reflect current deps
- **CLI help text** ↔ **README.md** examples: Keep command examples in sync
- **JSON schemas** ↔ **validation code**: Schema files must match validation logic

#### 3. Configuration & Settings
- **pyproject.toml**: 
  - Package name (eyelet on PyPI)
  - Script entry points
  - Dependencies and dev dependencies
  - Tool configurations (ruff, mypy, pytest)
- **src/eyelet/schemas/**: JSON schemas for validation
- **schemas/**: Root-level schema files (should match src/eyelet/schemas/)

#### 4. GitHub Actions & CI/CD
- **.github/workflows/**: All workflow files
- **pyproject.toml** build config ↔ GitHub Actions build steps
- **PyPI package name** consistency across workflows and documentation

#### 5. Import and Module Structure
- **src/eyelet/__init__.py**: Public API exports
- **src/eyelet/__main__.py**: CLI entry point
- **Import paths**: When refactoring, check all internal imports

### Maintenance Checklists

#### Before Every Release
1. [ ] Update version in pyproject.toml
2. [ ] Update version in src/eyelet/__init__.py  
3. [ ] Update CHANGELOG.md with new features/fixes
4. [ ] Verify all README examples work with current version
5. [ ] Run full test suite: `uv run pytest`
6. [ ] Check linting: `uv run ruff check .`
7. [ ] Test PyPI installation: `uvx eyelet --version`
8. [ ] Verify GitHub Actions are passing

#### Monthly Maintenance
1. [ ] Update dependencies in pyproject.toml
2. [ ] Review and clean up documentation for accuracy
3. [ ] Check for broken links in all .md files
4. [ ] Verify CLI help text matches documentation
5. [ ] Test on different platforms if possible

#### Code Quality Vigilance
- **Never leave TODO comments** without GitHub issues
- **Update docstrings** when changing function signatures
- **Keep test coverage** above 80% for new code
- **Remove unused imports** and dead code immediately
- **Update CLI completion** when adding new commands/options

### Anti-Patterns to Avoid
1. **Documentation Drift**: Always update docs when code changes
2. **Version Inconsistency**: Version numbers must be synchronized everywhere
3. **Dead Code**: Remove unused files, functions, and imports immediately
4. **Hardcoded Paths**: Use Path objects and make paths configurable
5. **Missing Error Handling**: Every file operation needs proper error handling
6. **Inconsistent Naming**: Follow eyelet/hook theme and Python conventions
7. **Circular Imports**: Keep clean separation between layers

### File Monitoring for Changes
When any of these files change, review related files:
- `pyproject.toml` → Check README.md, CHANGELOG.md, GitHub workflows
- `src/eyelet/cli/*.py` → Update help documentation, README examples  
- `schemas/*.json` → Update validation code and documentation
- `.github/workflows/*` → Test locally, update docs/setup/
- `src/eyelet/__init__.py` → Check all import statements across codebase