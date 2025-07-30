# Product Requirements Document: Eyelet - Hook Orchestration System

## Product Overview

Eyelet is a sophisticated Python-based CLI tool distributed via uvx that provides comprehensive management, templating, and execution handling for AI agent hooks. It abstracts hook actions into a powerful workflow system with robust logging, templating, and a beautiful TUI interface. Like a ship's eyelet that controls the sails, Eyelet controls and orchestrates your AI agent's behavior.

## Vision Statement

To create a unified, extensible hook management system that empowers developers to leverage AI agent hook capabilities through templates, workflows, and intelligent automation while maintaining complete observability of all hook executions.

## Core Features

### 1. Hook Configuration Management
- Configure Claude hooks at any scope (user or project level)
- Non-destructive configuration that complements existing hooks
- Direct integration with Claude's settings.json or CLI commands
- Support for all seven Claude Code hook types:
  - PreToolUse
  - PostToolUse
  - Notification
  - UserPromptSubmit
  - Stop
  - SubagentStop
  - PreCompact
- **Dynamic Hook Discovery System**
  - Automatic detection of new Claude Code tools
  - Generation of all valid hook/matcher combinations
  - Self-updating capability as Claude Code evolves
  - Documentation scraping and runtime discovery

### 2. Template System
- Deploy pre-defined hook patterns via templates
- Template library for common use cases
- Custom template creation and sharing
- Template parameters and variables
- Version control friendly template format

### 3. Universal Hook Endpoint
- Single CLI entry point for all hook executions
- Automatic request parsing and routing
- Context-aware execution handling
- Error handling and recovery
- Non-blocking execution (always returns 0 to avoid disrupting Claude)

### 4. Workflow Abstraction Layer
- Directory-based workflow organization
- Modular action handlers
- Chainable workflow steps
- Conditional execution paths
- Environment variable and context passing

### 5. Comprehensive Logging System
- SQLite database for high-volume logging
  - Optimized for write performance
  - Minimal validation overhead
  - JSON payload storage
- File-based logging alternative
  - Directory structure organization
  - Rotation and archival support
- Configurable logging levels and targets

### 6. TUI Interface (Textual)
- Interactive hook configuration
- Template browser and installer
- Log viewer and analyzer
- Workflow editor
- Real-time hook execution monitoring
- Beautiful, responsive terminal UI design

### 7. AI Integration
- Claude Code CLI/SDK integration for intelligent workflows
- AI-powered hook suggestions
- Automated workflow generation
- Context enhancement capabilities

## Technical Architecture

### Technology Stack
- **Language**: Python 3.11+
- **Distribution**: uv/uvx
- **TUI Framework**: Textual
- **CLI Framework**: Click
- **Database**: SQLite with SQLAlchemy
- **AI Integration**: Claude Code SDK (Python)

### Core Components

#### 1. CLI Structure
```
eyelet/
├── src/
│   └── eyelet/
│       ├── __init__.py
│       ├── __main__.py    # Entry point for uvx
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py    # Click CLI setup
│       │   ├── configure.py
│       │   ├── template.py
│       │   ├── execute.py
│       │   └── logs.py
│       ├── tui/
│       │   ├── __init__.py
│       │   └── app.py     # Textual TUI
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── hooks.py
│       │   └── discovery.py
│       ├── workflows/
│       │   └── engine.py
│       └── templates/
│           └── library/
├── workflows/              # User-defined workflows
├── pyproject.toml
└── README.md
```

#### 2. Hook Execution Flow
1. Claude Code invokes hook → CLI endpoint
2. Parse incoming JSON payload
3. Log execution to SQLite/filesystem
4. Determine workflow based on configuration
5. Execute workflow steps
6. Return success (exit 0)

#### 3. Workflow Directory Structure
```
workflows/
├── pre-tool-use/
│   ├── validation/
│   ├── enhancement/
│   └── monitoring/
├── post-tool-use/
│   ├── logging/
│   └── notifications/
└── custom/
    └── user-defined/
```

## Database Schema (SQLite)

```sql
-- Hook executions table
CREATE TABLE executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    hook_type TEXT NOT NULL,
    payload JSON NOT NULL,
    workflow TEXT,
    duration_ms INTEGER,
    status TEXT
);

-- Workflow results
CREATE TABLE workflow_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER,
    step_name TEXT,
    result JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(id)
);

-- Templates
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    content JSON NOT NULL,
    version TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## User Experience

### Installation
```bash
# Install with uvx (recommended)
uvx eyelet

# Or install with pipx
pipx install eyelet

# Or install from source
git clone https://github.com/bdmorin/eyelet
cd eyelet
uv pip install -e .
```

### Basic Usage
```bash
# Launch TUI - "All hands to the eyelet!"
eyelet

# Configure hooks for current project
eyelet configure --scope project

# Install a template
eyelet template install observability

# View logs
eyelet logs --tail 50

# Execute as hook endpoint
eyelet execute

# Discover available hooks
eyelet discover hooks

# Generate all hook combinations
eyelet generate matrix

# Update hook registry - "Check the charts"
eyelet update check
```

### TUI Workflows
1. **Main Menu**
   - Configure Hooks
   - Browse Templates
   - View Logs
   - Edit Workflows
   - Settings

2. **Hook Configuration**
   - Visual hook editor
   - Drag-and-drop workflow assignment
   - Test hook execution
   - Preview changes

3. **Template Browser**
   - Search and filter templates
   - Preview template contents
   - One-click installation
   - Template customization

## Integration Points

### Claude Code Settings
- Read/modify `.claude/settings.json`
- Preserve existing configurations
- Support for both user and project scopes
- Backup and restore functionality

### Claude CLI/SDK
- Execute Claude commands from workflows
- Parse Claude responses
- Context injection
- Python SDK integration

## Success Metrics
- Zero disruption to Claude Code operations
- Sub-10ms hook execution overhead
- 100% capture rate for hook executions
- Intuitive TUI with <3 click common operations
- Template adoption rate >50%

## Constraints
- Must never block Claude Code execution
- Minimal performance impact
- Cross-platform compatibility (macOS, Linux, Windows)
- No external service dependencies for core functionality
- Respect user privacy (local-only by default)

## Future Enhancements
- Web dashboard for remote monitoring
- Hook execution replay
- A/B testing for workflows
- Community template marketplace
- Webhook integrations
- Performance analytics
- Multi-agent coordination support

## Development Phases

### Phase 1: Core Foundation (Weeks 1-2)
- Basic CLI structure
- Hook execution handler
- SQLite logging
- Simple workflow execution

### Phase 2: TUI Development (Weeks 3-4)
- Textual TUI implementation
- Basic configuration interface
- Log viewer
- Template browser

### Phase 3: Advanced Features (Weeks 5-6)
- AI integration
- Complex workflow support
- Template engine
- Performance optimization

### Phase 4: Polish & Release (Week 7-8)
- Documentation
- Testing
- Package distribution
- Community templates