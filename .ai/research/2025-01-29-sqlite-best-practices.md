# SQLite Best Practices Research for High-Concurrency Logging (2025)

## Executive Summary

Based on extensive research into current best practices for SQLite in Python applications, this document provides recommendations for implementing a high-concurrency logging system for the eyelet/rigging project. The key findings indicate that for our use case (multiple processes writing simultaneously, high insert volume, minimal queries), a combination of **APSW or sqlite3** with **WAL mode** and **proper retry logic** will provide the best performance.

## Library Comparison

### Performance Rankings (100k insert benchmark)
1. **sqlite3 (raw)**: 0.201 seconds ⭐ FASTEST
2. **APSW**: Similar to sqlite3, better for complex queries
3. **SQLAlchemy Core**: 0.403 seconds
4. **SQLAlchemy ORM**: 0.640-8.067 seconds (depending on mode)
5. **Peewee**: 13.342 seconds ⭐ SLOWEST

### Recommendation: APSW or sqlite3

For our logging use case, I recommend using either **APSW** or **sqlite3** (stdlib):

**APSW Advantages:**
- Full SQLite feature access including JSON1, FTS5, virtual tables
- Better performance on complex queries (linear vs exponential growth)
- Built-in best practices configuration (`apsw.bestpractice`)
- Thread-safe connections without additional locking
- Better debugging and tracing capabilities

**sqlite3 Advantages:**
- Standard library (no additional dependencies)
- DBAPI compliant
- Sufficient for our simple insert/query needs
- Well-documented and widely understood

**Decision:** Start with **sqlite3** for simplicity, migrate to **APSW** if we need advanced features or hit performance issues.

## Connection Pooling & Multi-Process Handling

### Key Insight: SQLite's Limitation
SQLite allows multiple readers but only ONE writer at a time. For multi-process scenarios:

```python
# DON'T use connection pools for multi-process
# Each process should have its own connection
# SQLite handles locking at the file level
```

### Recommended Pattern: Process-Local Connections

```python
import sqlite3
import os
from pathlib import Path

class ProcessLocalConnection:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._pid = None
        self._conn = None
    
    @property
    def connection(self):
        # Create new connection if process changed (fork)
        if self._pid != os.getpid():
            if self._conn:
                self._conn.close()
            self._conn = self._create_connection()
            self._pid = os.getpid()
        return self._conn
    
    def _create_connection(self):
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=60.0,  # High timeout for concurrency
            isolation_level=None  # Autocommit mode
        )
        # Apply optimizations
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -64000")  # 64MB
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA mmap_size = 268435456")  # 256MB
        conn.execute("PRAGMA busy_timeout = 60000")  # 60s
        return conn
```

## Retry Logic with Exponential Backoff

### Enhanced Retry Implementation

```python
import random
import time
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')

def sqlite_retry(
    max_attempts: int = 5,
    base_delay: float = 0.1,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> Callable:
    """Decorator for SQLite operations with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Add randomization to prevent thundering herd
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    last_exception = e
                    if "locked" not in str(e).lower() or attempt == max_attempts - 1:
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random())
                    
                    time.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

# Usage example
@sqlite_retry(max_attempts=10, base_delay=0.05)
def insert_log(conn, log_data):
    conn.execute(
        "INSERT INTO logs (timestamp, data) VALUES (?, ?)",
        (time.time(), json.dumps(log_data))
    )
```

## JSON Storage Optimization

### JSON1 Extension Updates (2024)

Starting with SQLite 3.45.0 (January 2024), SQLite supports **JSONB** format:
- Binary JSON representation stored as BLOB
- Faster operations (no parsing overhead)
- Slightly less disk space
- Available by default in Python 3.9+ (Windows) and 3.7+ (macOS)

### Optimized Schema for JSON + Indexed Fields

```sql
-- Modern schema with JSONB support
CREATE TABLE hook_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Indexed fields for fast queries
    timestamp REAL NOT NULL,
    timestamp_iso TEXT GENERATED ALWAYS AS (datetime(timestamp, 'unixepoch')) STORED,
    session_id TEXT NOT NULL,
    hook_type TEXT NOT NULL,
    tool_name TEXT,
    status TEXT,
    
    -- Metadata fields
    hostname TEXT,
    project_dir TEXT,
    
    -- JSONB for efficient storage and querying
    data BLOB NOT NULL CHECK(json_valid(data)),
    
    -- Generated columns for common JSON extracts
    user_id TEXT GENERATED ALWAYS AS (json_extract(data, '$.user_id')) STORED,
    error_code TEXT GENERATED ALWAYS AS (json_extract(data, '$.error.code')) STORED
);

-- Indexes for performance
CREATE INDEX idx_timestamp ON hook_logs(timestamp);
CREATE INDEX idx_session_id ON hook_logs(session_id);
CREATE INDEX idx_hook_type ON hook_logs(hook_type);
CREATE INDEX idx_tool_name ON hook_logs(tool_name) WHERE tool_name IS NOT NULL;
CREATE INDEX idx_status ON hook_logs(status);
CREATE INDEX idx_user_id ON hook_logs(user_id) WHERE user_id IS NOT NULL;

-- Partial index for error queries
CREATE INDEX idx_errors ON hook_logs(timestamp, error_code) 
    WHERE status = 'error' AND error_code IS NOT NULL;
```

### Storing and Querying JSON Data

```python
# Store as JSONB (automatic in SQLite 3.45.0+)
def insert_hook_log(conn, hook_data: dict):
    conn.execute("""
        INSERT INTO hook_logs (
            timestamp, session_id, hook_type, tool_name, 
            status, hostname, project_dir, data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, json(?))
    """, (
        hook_data['timestamp'],
        hook_data['session_id'],
        hook_data['hook_type'],
        hook_data.get('tool_name'),
        hook_data.get('status', 'unknown'),
        socket.gethostname(),
        os.getcwd(),
        json.dumps(hook_data)  # SQLite converts to JSONB internally
    ))

# Efficient JSON queries
def query_errors_by_code(conn, error_code: str, limit: int = 100):
    return conn.execute("""
        SELECT 
            timestamp_iso,
            hook_type,
            json_extract(data, '$.error.message') as error_message,
            json_extract(data, '$.error.traceback') as traceback
        FROM hook_logs
        WHERE error_code = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (error_code, limit)).fetchall()
```

## Schema Migration Strategy

### Recommendation: Lightweight Approach

For our logging use case, I recommend a **lightweight migration approach** rather than heavy tools like Alembic:

```python
# migrations.py
MIGRATIONS = [
    # Version 1: Initial schema
    (1, """
        CREATE TABLE hook_logs (...);
        CREATE INDEX idx_timestamp ON hook_logs(timestamp);
    """),
    
    # Version 2: Add error_code column
    (2, """
        ALTER TABLE hook_logs ADD COLUMN error_code TEXT 
            GENERATED ALWAYS AS (json_extract(data, '$.error.code')) STORED;
        CREATE INDEX idx_error_code ON hook_logs(error_code) 
            WHERE error_code IS NOT NULL;
    """),
]

def migrate_database(conn):
    """Apply migrations using PRAGMA user_version."""
    current_version = conn.execute("PRAGMA user_version").fetchone()[0]
    
    for version, migration_sql in MIGRATIONS:
        if version > current_version:
            conn.executescript(migration_sql)
            conn.execute(f"PRAGMA user_version = {version}")
            print(f"Applied migration {version}")
```

## Performance Optimizations

### 1. Write-Ahead Logging (WAL) Configuration

```python
# Optimal WAL settings for logging
conn.execute("PRAGMA journal_mode = WAL")
conn.execute("PRAGMA wal_autocheckpoint = 1000")  # Checkpoint every 1000 pages
conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")   # Manual checkpoint on startup
```

### 2. Batch Inserts for High Volume

```python
import queue
import threading
from typing import List, Dict

class BatchLogger:
    def __init__(self, db_path: Path, batch_size: int = 100, flush_interval: float = 1.0):
        self.db_path = db_path
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.start()
    
    def log(self, data: Dict):
        """Add log entry to queue."""
        self.queue.put(data)
    
    def _worker(self):
        """Background worker for batch inserts."""
        conn = create_optimized_connection(self.db_path)
        
        while not self.stop_event.is_set():
            batch = []
            deadline = time.time() + self.flush_interval
            
            # Collect batch
            while len(batch) < self.batch_size and time.time() < deadline:
                try:
                    timeout = max(0, deadline - time.time())
                    item = self.queue.get(timeout=timeout)
                    batch.append(item)
                except queue.Empty:
                    break
            
            # Insert batch
            if batch:
                self._insert_batch(conn, batch)
    
    @sqlite_retry(max_attempts=10)
    def _insert_batch(self, conn, batch: List[Dict]):
        """Insert batch with retry logic."""
        with conn:
            conn.executemany("""
                INSERT INTO hook_logs (
                    timestamp, session_id, hook_type, tool_name,
                    status, hostname, project_dir, data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, json(?))
            """, [
                (
                    item['timestamp'],
                    item['session_id'],
                    item['hook_type'],
                    item.get('tool_name'),
                    item.get('status', 'unknown'),
                    socket.gethostname(),
                    os.getcwd(),
                    json.dumps(item)
                )
                for item in batch
            ])
```

### 3. Real-time Dashboard Considerations

For the real-time dashboard requirement:

```python
# Use a separate read-only connection with different settings
def create_readonly_connection(db_path: Path):
    """Create optimized read-only connection for dashboard."""
    conn = sqlite3.connect(
        f"file:{db_path}?mode=ro",
        uri=True,
        timeout=5.0
    )
    conn.execute("PRAGMA query_only = ON")
    conn.execute("PRAGMA cache_size = -32000")  # 32MB cache for queries
    conn.row_factory = sqlite3.Row  # Dict-like access
    return conn

# Efficient query for dashboard updates
def get_recent_logs(conn, since_timestamp: float, limit: int = 1000):
    """Get logs since timestamp for dashboard updates."""
    return conn.execute("""
        SELECT 
            id,
            timestamp_iso,
            hook_type,
            tool_name,
            status,
            json_extract(data, '$.duration_ms') as duration_ms,
            json_extract(data, '$.error.message') as error_message
        FROM hook_logs
        WHERE timestamp > ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (since_timestamp, limit)).fetchall()
```

## Arbitrary Data Logging

For the requirement to log arbitrary data (GitHub repo, custom metadata):

```python
# Flexible schema with custom fields
class HookLogger:
    def __init__(self, db_path: Path, custom_fields: Dict[str, Any] = None):
        self.db_path = db_path
        self.custom_fields = custom_fields or {}
    
    def log(self, hook_type: str, **kwargs):
        """Log with arbitrary fields."""
        data = {
            'timestamp': time.time(),
            'session_id': self.get_session_id(),
            'hook_type': hook_type,
            'hostname': socket.gethostname(),
            'custom_fields': self.custom_fields,
            **kwargs
        }
        
        # Auto-detect and add contextual data
        if git_repo := self._detect_git_repo():
            data['git'] = git_repo
        
        if env_vars := self._get_relevant_env_vars():
            data['environment'] = env_vars
        
        self._insert_log(data)
    
    def _detect_git_repo(self) -> Optional[Dict[str, str]]:
        """Detect git repository information."""
        try:
            import subprocess
            result = {}
            
            # Get current branch
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                text=True
            ).strip()
            result['branch'] = branch
            
            # Get current commit
            commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                text=True
            ).strip()
            result['commit'] = commit
            
            # Get remote URL
            remote = subprocess.check_output(
                ['git', 'config', '--get', 'remote.origin.url'],
                text=True
            ).strip()
            result['remote'] = remote
            
            return result
        except:
            return None
```

## Summary of Recommendations

1. **Library**: Use `sqlite3` (stdlib) initially, consider `APSW` for advanced features
2. **Concurrency**: Process-local connections with 60s timeout
3. **Retry Logic**: Exponential backoff with jitter (0.05s base, 10 attempts)
4. **JSON Storage**: Use JSONB with generated columns for indexed fields
5. **Schema Migrations**: Lightweight PRAGMA user_version approach
6. **Performance**: WAL mode, batch inserts, separate read connections
7. **Arbitrary Data**: Store in JSON with automatic context detection

## Code Example: Complete Implementation

```python
# sqlite_logger.py
import json
import sqlite3
import time
import socket
import random
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import wraps
from contextlib import contextmanager

class HighConcurrencySQLiteLogger:
    """Production-ready SQLite logger for multi-process environments."""
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS hook_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        timestamp_iso TEXT GENERATED ALWAYS AS (datetime(timestamp, 'unixepoch')) STORED,
        session_id TEXT NOT NULL,
        hook_type TEXT NOT NULL,
        tool_name TEXT,
        status TEXT,
        hostname TEXT,
        project_dir TEXT,
        data BLOB NOT NULL CHECK(json_valid(data)),
        
        -- Generated columns for common queries
        duration_ms INTEGER GENERATED ALWAYS AS (
            CAST(json_extract(data, '$.execution.duration_ms') AS INTEGER)
        ) STORED,
        error_code TEXT GENERATED ALWAYS AS (
            json_extract(data, '$.error.code')
        ) STORED
    );
    
    -- Performance indexes
    CREATE INDEX IF NOT EXISTS idx_timestamp ON hook_logs(timestamp);
    CREATE INDEX IF NOT EXISTS idx_session_id ON hook_logs(session_id);
    CREATE INDEX IF NOT EXISTS idx_hook_type ON hook_logs(hook_type);
    CREATE INDEX IF NOT EXISTS idx_tool_name ON hook_logs(tool_name) WHERE tool_name IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_errors ON hook_logs(timestamp, error_code) 
        WHERE status = 'error' AND error_code IS NOT NULL;
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database with schema and optimizations."""
        with self._get_connection() as conn:
            # Apply schema
            conn.executescript(self.SCHEMA)
            
            # Set optimal pragmas
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("PRAGMA mmap_size = 268435456")
            conn.execute("PRAGMA wal_autocheckpoint = 1000")
    
    @contextmanager
    def _get_connection(self):
        """Get a connection with optimal settings."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=60.0,
            isolation_level=None  # Autocommit
        )
        try:
            yield conn
        finally:
            conn.close()
    
    def _retry_with_backoff(self, func, max_attempts=10):
        """Execute function with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func()
            except sqlite3.OperationalError as e:
                last_exception = e
                if "locked" not in str(e).lower() or attempt == max_attempts - 1:
                    raise
                
                # Exponential backoff with jitter
                delay = min(0.05 * (2 ** attempt), 10.0)
                delay *= (0.5 + random.random())
                time.sleep(delay)
        
        raise last_exception
    
    def log(self, hook_data: Dict[str, Any]) -> bool:
        """Log hook data with retry logic."""
        def _insert():
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO hook_logs (
                        timestamp, session_id, hook_type, tool_name,
                        status, hostname, project_dir, data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, json(?))
                """, (
                    hook_data.get('timestamp', time.time()),
                    hook_data['session_id'],
                    hook_data['hook_type'],
                    hook_data.get('tool_name'),
                    hook_data.get('status', 'unknown'),
                    socket.gethostname(),
                    hook_data.get('cwd', os.getcwd()),
                    json.dumps(hook_data)
                ))
        
        try:
            self._retry_with_backoff(_insert)
            return True
        except Exception as e:
            print(f"Failed to log after retries: {e}")
            return False
```

This research provides a comprehensive foundation for implementing a robust, high-performance SQLite logging system for the eyelet/rigging project.