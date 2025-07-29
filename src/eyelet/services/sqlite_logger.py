"""SQLite logging implementation with retry logic."""

import json
import socket
from datetime import datetime
from pathlib import Path
from typing import Any

from eyelet.domain.hooks import HookData
from eyelet.services.sqlite_connection import ProcessLocalConnection, sqlite_retry


class SQLiteLogger:
    """SQLite logger with best practices for high-concurrency logging."""

    # Database schema with modern SQLite features
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
        -- Store as BLOB for JSONB optimization in SQLite 3.45+
        data BLOB NOT NULL CHECK(json_valid(data)),
        -- Generated columns for frequently queried JSON fields
        error_code TEXT GENERATED ALWAYS AS (json_extract(data, '$.execution.error_message')) STORED,
        git_branch TEXT GENERATED ALWAYS AS (json_extract(data, '$.metadata.git_branch')) STORED
    );

    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_timestamp ON hooks(timestamp);
    CREATE INDEX IF NOT EXISTS idx_session_id ON hooks(session_id);
    CREATE INDEX IF NOT EXISTS idx_hook_type ON hooks(hook_type);
    CREATE INDEX IF NOT EXISTS idx_tool_name ON hooks(tool_name);
    CREATE INDEX IF NOT EXISTS idx_project_dir ON hooks(project_dir);
    CREATE INDEX IF NOT EXISTS idx_error_code ON hooks(error_code) WHERE error_code IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_git_branch ON hooks(git_branch) WHERE git_branch IS NOT NULL;

    -- Composite index for time-based queries by type
    CREATE INDEX IF NOT EXISTS idx_type_timestamp ON hooks(hook_type, timestamp DESC);
    """

    def __init__(self, db_path: Path):
        """Initialize SQLite logger.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._conn_manager = ProcessLocalConnection(db_path)
        self._initialize_db()

    @sqlite_retry(max_attempts=5)
    def _initialize_db(self) -> None:
        """Initialize database with schema."""
        conn = self._conn_manager.connection
        conn.executescript(self.SCHEMA)

        # Set initial schema version
        current_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if current_version == 0:
            conn.execute("PRAGMA user_version = 1")

    def _get_hostname(self) -> str:
        """Get hostname safely."""
        try:
            return socket.gethostname()
        except Exception:
            return "unknown"

    def _get_ip_address(self) -> str:
        """Get IP address safely."""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return "unknown"

    @sqlite_retry(max_attempts=10, base_delay=0.05)
    def log_hook(self, hook_data: HookData) -> bool:
        """Log hook data to SQLite with automatic retry.

        Args:
            hook_data: Hook data to log

        Returns:
            True if successful, False otherwise

        Raises:
            sqlite3.OperationalError: If database is locked after all retries
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

        # Full data as JSON (with Path conversion)
        data_dict = hook_data.model_dump()
        # Convert Path objects to strings
        if "cwd" in data_dict and hasattr(data_dict["cwd"], "__fspath__"):
            data_dict["cwd"] = str(data_dict["cwd"])
        data_json = json.dumps(data_dict, default=str)

        # SQL insert statement
        sql = """
        INSERT INTO hooks (
            timestamp, timestamp_iso, session_id, hook_type, tool_name,
            status, duration_ms, hostname, ip_address, project_dir, data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            timestamp,
            timestamp_iso,
            session_id,
            hook_type,
            tool_name,
            status,
            duration_ms,
            hostname,
            ip_address,
            project_dir,
            data_json,
        )

        try:
            conn = self._conn_manager.connection
            conn.execute(sql, values)
            return True
        except Exception:
            # Re-raise to trigger retry decorator
            raise

    def query_hooks(
        self,
        hook_type: str | None = None,
        tool_name: str | None = None,
        session_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
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

        conn = self._conn_manager.connection
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def batch_insert(self, hook_data_list: list[HookData]) -> int:
        """Batch insert multiple hook records for better performance.

        Args:
            hook_data_list: List of hook data to insert

        Returns:
            Number of records inserted
        """
        if not hook_data_list:
            return 0

        sql = """
        INSERT INTO hooks (
            timestamp, timestamp_iso, session_id, hook_type, tool_name,
            status, duration_ms, hostname, ip_address, project_dir, data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values_list = []
        for hook_data in hook_data_list:
            values = (
                hook_data.timestamp_unix,
                hook_data.timestamp,
                hook_data.session_id,
                hook_data.hook_type,
                hook_data.tool_name or None,
                hook_data.execution.status if hook_data.execution else "unknown",
                hook_data.execution.duration_ms if hook_data.execution else None,
                self._get_hostname(),
                self._get_ip_address(),
                str(hook_data.cwd),
                json.dumps(hook_data.model_dump()),
            )
            values_list.append(values)

        @sqlite_retry(max_attempts=10)
        def _batch_insert():
            conn = self._conn_manager.connection
            with conn:
                conn.executemany(sql, values_list)
            return len(values_list)

        return _batch_insert()
