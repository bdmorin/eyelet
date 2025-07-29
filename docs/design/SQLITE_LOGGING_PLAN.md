# SQLite Logging Implementation Plan

## Overview

Transition from JSON file logging to SQLite database with support for concurrent writes from multiple Claude Code instances.

## Architecture Decisions

### 1. Write Strategy
- **Approach**: Simple retry with exponential backoff
- **No daemon**: Each hook process opens/closes its own connection
- **Concurrency**: WAL mode + application-level retry logic

### 2. Logging Scope
- **Options**: `project`, `global`, or `both`
- **Global path**: `~/.claude/eyelet-logging/`
- **Project path**: `.eyelet-logging/` (configurable)
- **Auto-gitignore**: Add logging directory to .gitignore

### 3. Database Schema
```sql
CREATE TABLE hooks (
    id INTEGER PRIMARY KEY,
    timestamp REAL NOT NULL,
    session_id TEXT NOT NULL,
    hook_type TEXT NOT NULL,
    tool_name TEXT,
    status TEXT,
    duration_ms INTEGER,
    -- Extensible metadata
    hostname TEXT,
    ip_address TEXT,
    -- Full JSON for flexibility
    data JSON NOT NULL
);

-- Indexes for common queries
CREATE INDEX idx_timestamp ON hooks(timestamp);
CREATE INDEX idx_session_id ON hooks(session_id);
CREATE INDEX idx_hook_type ON hooks(hook_type);
CREATE INDEX idx_tool_name ON hooks(tool_name);
```

### 4. Configuration Files

**Global**: `~/.claude/eyelet.yaml`
```yaml
logging:
  format: json  # 'json' or 'sqlite' 
  enabled: true
  scope: project  # 'project', 'global', or 'both'
  global_path: ~/.claude/eyelet-logging
  project_path: .eyelet-logging
  add_to_gitignore: true

metadata:
  include_hostname: true
  include_ip: true
```

**Project**: `./eyelet.yaml`
```yaml
logging:
  format: sqlite  # Override global
  scope: both     # Override global
  path: .eyelet-logs  # Override default project path
```

### 5. SQLite Optimizations
```python
# Connection settings for high concurrency
PRAGMAS = [
    "PRAGMA journal_mode = WAL",
    "PRAGMA synchronous = normal", 
    "PRAGMA cache_size = -64000",
    "PRAGMA temp_store = memory",
    "PRAGMA mmap_size = 268435456",
    "PRAGMA busy_timeout = 10000"
]
```

## Implementation Plan

1. **Default Format**: Start with JSON (simpler, no concurrency issues)
2. **SQLite Opt-in**: Users can enable via config
3. **Multiple Hooks**: Support multiple commands per hook type
4. **Doctor Command**: Validate and fix configuration mismatches

## CLI Commands

```bash
# Configuration
uvx eyelet config --global --set logging.format sqlite
uvx eyelet config --set logging.scope both

# Diagnostics
uvx eyelet doctor
uvx eyelet doctor --fix

# Clear logs
uvx eyelet clear --all
uvx eyelet clear --project
```

## Next Steps

1. Implement configuration file management
2. Create SQLite database layer with retry logic
3. Build `eyelet doctor` command
4. Add query interface for both JSON and SQLite
5. Create browser-based query interface

## Future Roadmap

- Enhanced metadata system with dynamic fields
- Metadata CLI commands for easy customization
- Migration tools between JSON and SQLite
- Advanced query and analytics features