# SQLite Implementation Documentation

## Overview

Eyelet's SQLite implementation provides high-performance, concurrent logging for multiple Claude Code instances with rich metadata and powerful query capabilities. The system supports flexible logging formats (JSON files, SQLite, or both) based on user configuration.

## Architecture

### 1. Connection Management (`sqlite_connection.py`)

**Process-Local Connections**
- Each process maintains its own connection (fork-safe)
- Automatically recreates connection when process ID changes
- No shared connection pool between processes (avoids multi-process issues)

```python
class ProcessLocalConnection:
    def __init__(self, db_path: Path):
        self._pid = None
        self._conn = None
    
    @property
    def connection(self):
        if self._pid != os.getpid():
            # New process detected, create new connection
            self._conn = self._create_connection()
            self._pid = os.getpid()
        return self._conn
```

**Optimizations Applied**
- WAL mode for concurrent reads/writes
- 64MB cache size
- Memory-mapped I/O (256MB)
- 60-second busy timeout
- Autocommit mode for logging

### 2. Retry Logic

**Exponential Backoff with Jitter**
```python
@sqlite_retry(max_attempts=10, base_delay=0.05)
def log_hook(self, hook_data: HookData) -> bool:
    # Automatic retry on database lock
```

- Base delay: 50ms
- Exponential growth: 0.05s → 0.1s → 0.2s → 0.4s → 0.8s...
- Random jitter prevents thundering herd
- Maximum 10 attempts before failure

### 3. Database Schema

**Hybrid Design**: Indexed fields + full JSON data

```sql
CREATE TABLE hooks (
    -- Core indexed fields for fast queries
    id INTEGER PRIMARY KEY,
    timestamp REAL NOT NULL,
    session_id TEXT NOT NULL,
    hook_type TEXT NOT NULL,
    tool_name TEXT,
    status TEXT,
    
    -- Metadata fields
    hostname TEXT,
    ip_address TEXT,
    project_dir TEXT,
    
    -- Full data as BLOB (JSONB optimization)
    data BLOB NOT NULL CHECK(json_valid(data)),
    
    -- Generated columns for JSON fields
    error_code TEXT GENERATED ALWAYS AS 
        (json_extract(data, '$.execution.error_message')) STORED,
    git_branch TEXT GENERATED ALWAYS AS 
        (json_extract(data, '$.metadata.git.branch')) STORED
);
```

**Indexes**
- Single column indexes on core fields
- Composite index for time-based queries: `(hook_type, timestamp DESC)`
- Conditional indexes on generated columns

### 4. Logging Flow

```
1. Hook Triggered → execute.py
2. ConfigService loads eyelet.yaml settings
3. HookLogger determines format (json/sqlite/both) and scope (project/global/both)
4. For SQLite:
   - GitMetadata enriches log data
   - SQLiteLogger writes with retry logic
   - ProcessLocalConnection handles concurrency
5. For JSON:
   - Traditional file-based logging to eyelet-hooks/
```

### 5. Query System (`query_service.py`)

**Flexible Filtering**
- By hook type, tool name, session ID
- Time-based (since/until)
- By status, git branch, error presence
- Full-text search across JSON data

**CLI Commands**
```bash
# Search with filters
eyelet query search --hook-type PreToolUse --tool Bash --since 1h

# Summary statistics
eyelet query summary --since 24h

# Recent errors
eyelet query errors --limit 10

# Session timeline
eyelet query session <session-id>

# Search in data
eyelet query grep "git push"
```

### 6. Configuration (`eyelet.yaml`)

**Global Configuration** (`~/.claude/eyelet.yaml`)
```yaml
logging:
  format: json      # json, sqlite, or both
  enabled: true
  scope: project    # project, global, or both
  global_path: ~/.claude/eyelet-logging
  project_path: .eyelet-logging
  add_to_gitignore: true

metadata:
  include_hostname: true
  include_ip: true
  custom_fields:
    team: engineering
```

**Project Override** (`./eyelet.yaml`)
```yaml
logging:
  format: sqlite    # Override to use SQLite
  scope: both       # Log to both locations
```

## Performance Characteristics

### Write Performance
- Single insert: ~5-10ms with retry logic
- Batch insert: 100-200 inserts/second
- Concurrent writes: Handled via WAL mode + retry
- Lock contention: Mitigated by exponential backoff

### Query Performance
- Indexed queries: <10ms for most operations
- Full-text search: Linear scan (optimizable with FTS5)
- Summary statistics: ~50ms for 10,000 records

### Storage
- Overhead: ~1KB per log entry
- Compression: Via BLOB storage for JSON
- Growth rate: ~100MB per 100,000 hooks

## Migration Strategy

Schema migrations use SQLite's `PRAGMA user_version`:

```python
MIGRATIONS = [
    (1, "Initial schema", "..."),
    (2, "Add user_id column", "ALTER TABLE hooks ADD COLUMN user_id TEXT;")
]

def migrate_database(conn):
    current_version = conn.execute("PRAGMA user_version").fetchone()[0]
    for version, description, sql in MIGRATIONS:
        if version > current_version:
            conn.executescript(sql)
            conn.execute(f"PRAGMA user_version = {version}")
```

## Monitoring & Health

**Database Health Checks**
- Integrity verification
- WAL file size monitoring
- Table statistics and growth tracking
- Index usage analysis

**Performance Monitoring**
- Insert/query timing statistics
- Retry counts and lock wait times
- Success rates and error tracking

## Security Considerations

1. **Git Credentials**: Sanitized from remote URLs
2. **Environment Variables**: Only CLAUDE*/EYELET* vars logged
3. **File Permissions**: Database created with user-only access
4. **SQL Injection**: Parameterized queries throughout

## Future Enhancements

1. **Full-Text Search**: Add FTS5 for better search performance
2. **Compression**: zlib compression for older entries
3. **Partitioning**: Time-based partitioning for large databases
4. **Replication**: Optional sync to remote database
5. **Analytics**: Pre-computed statistics tables
6. **Retention**: Automatic cleanup of old entries