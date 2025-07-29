"""SQLite logging implementation with retry logic."""

import json
import sqlite3
import time
import socket
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from eyelet.domain.hooks import HookData


class SQLiteLogger:
    """SQLite logger with exponential backoff retry logic."""
    
    # SQLite pragmas for optimal performance
    PRAGMAS = [
        "PRAGMA journal_mode = WAL",
        "PRAGMA synchronous = normal",
        "PRAGMA cache_size = -64000",      # 64MB cache
        "PRAGMA temp_store = memory",
        "PRAGMA mmap_size = 268435456",    # 256MB memory-mapped I/O
        "PRAGMA busy_timeout = 10000"      # 10 second timeout
    ]
    
    # Database schema
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS hooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        timestamp_iso TEXT NOT NULL,
        session_id TEXT NOT NULL,
        hook_type TEXT NOT NULL,
        tool_name TEXT,
        status TEXT,
        duration_ms INTEGER,
        hostname TEXT,
        ip_address TEXT,
        project_dir TEXT,
        data JSON NOT NULL
    );
    
    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_timestamp ON hooks(timestamp);
    CREATE INDEX IF NOT EXISTS idx_session_id ON hooks(session_id);
    CREATE INDEX IF NOT EXISTS idx_hook_type ON hooks(hook_type);
    CREATE INDEX IF NOT EXISTS idx_tool_name ON hooks(tool_name);
    CREATE INDEX IF NOT EXISTS idx_project_dir ON hooks(project_dir);
    """
    
    def __init__(self, db_path: Path):
        """Initialize SQLite logger.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize database with schema."""
        with self._get_connection() as conn:
            conn.executescript(self.SCHEMA)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with optimized settings."""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        
        # Apply performance pragmas
        for pragma in self.PRAGMAS:
            conn.execute(pragma)
        
        return conn
    
    def _get_hostname(self) -> str:
        """Get hostname safely."""
        try:
            return socket.gethostname()
        except:
            return "unknown"
    
    def _get_ip_address(self) -> str:
        """Get IP address safely."""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "unknown"
    
    def log_hook(self, hook_data: HookData, max_retries: int = 5) -> bool:
        """Log hook data to SQLite with retry logic.
        
        Args:
            hook_data: Hook data to log
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        # Extract core fields for indexing
        timestamp = hook_data.timestamp_unix
        timestamp_iso = hook_data.timestamp
        session_id = hook_data.session_id
        hook_type = hook_data.hook_type
        tool_name = hook_data.tool_name or None
        status = hook_data.execution.status if hook_data.execution else "unknown"
        duration_ms = hook_data.execution.duration_ms if hook_data.execution else None
        hostname = self._get_hostname()
        ip_address = self._get_ip_address()
        project_dir = str(hook_data.cwd)
        
        # Full data as JSON
        data_json = json.dumps(hook_data.model_dump())
        
        # SQL insert statement
        sql = """
        INSERT INTO hooks (
            timestamp, timestamp_iso, session_id, hook_type, tool_name,
            status, duration_ms, hostname, ip_address, project_dir, data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            timestamp, timestamp_iso, session_id, hook_type, tool_name,
            status, duration_ms, hostname, ip_address, project_dir, data_json
        )
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                with self._get_connection() as conn:
                    conn.execute(sql, values)
                    conn.commit()
                return True
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    # Exponential backoff: 0.1s, 0.2s, 0.4s, 0.8s, 1.6s
                    wait_time = 0.1 * (2 ** attempt)
                    time.sleep(wait_time)
                else:
                    # Log error but don't crash
                    print(f"SQLite error after {attempt + 1} attempts: {e}")
                    return False
            except Exception as e:
                print(f"Unexpected error logging to SQLite: {e}")
                return False
        
        return False
    
    def query_hooks(
        self,
        hook_type: Optional[str] = None,
        tool_name: Optional[str] = None,
        session_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """Query hooks from database.
        
        Args:
            hook_type: Filter by hook type
            tool_name: Filter by tool name
            session_id: Filter by session ID
            since: Filter by timestamp (hooks after this time)
            limit: Maximum number of results
            
        Returns:
            List of hook records
        """
        conditions = []
        params = []
        
        if hook_type:
            conditions.append("hook_type = ?")
            params.append(hook_type)
        
        if tool_name:
            conditions.append("tool_name = ?")
            params.append(tool_name)
        
        if session_id:
            conditions.append("session_id = ?")
            params.append(session_id)
        
        if since:
            conditions.append("timestamp > ?")
            params.append(since.timestamp())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
        SELECT * FROM hooks
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT ?
        """
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]