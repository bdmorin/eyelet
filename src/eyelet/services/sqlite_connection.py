"""Process-local SQLite connection management with best practices."""

import os
import random
import sqlite3
import time
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any


class ProcessLocalConnection:
    """Thread-safe, process-local SQLite connection manager.

    Handles fork safety by creating new connections when process ID changes.
    This is critical for multi-process scenarios like multiple Claude Code instances.
    """

    def __init__(self, db_path: Path):
        """Initialize connection manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._pid: int | None = None
        self._conn: sqlite3.Connection | None = None

    def _create_connection(self) -> sqlite3.Connection:
        """Create optimized SQLite connection with best practices."""
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Open connection with URI mode for better control
        conn = sqlite3.connect(
            f"file:{self.db_path}?mode=rwc",  # Read-write-create
            uri=True,
            timeout=60.0,  # High timeout for busy environments
            isolation_level=None,  # Autocommit mode for logging
        )

        # Enable optimizations
        optimizations = [
            "PRAGMA journal_mode = WAL",  # Write-Ahead Logging
            "PRAGMA synchronous = NORMAL",  # Balance safety/speed
            "PRAGMA cache_size = -64000",  # 64MB cache
            "PRAGMA temp_store = MEMORY",  # RAM for temp tables
            "PRAGMA mmap_size = 268435456",  # 256MB memory-mapped I/O
            "PRAGMA busy_timeout = 60000",  # 60s timeout
            "PRAGMA wal_autocheckpoint = 1000",  # Checkpoint every 1000 pages
        ]

        for pragma in optimizations:
            conn.execute(pragma)

        # Enable JSON1 extension features
        conn.row_factory = sqlite3.Row

        return conn

    @property
    def connection(self) -> sqlite3.Connection:
        """Get connection, creating new one if process changed."""
        current_pid = os.getpid()

        # Create new connection if process changed (fork safety)
        if self._pid != current_pid:
            if self._conn:
                try:
                    self._conn.close()
                except Exception:
                    pass
            self._conn = self._create_connection()
            self._pid = current_pid

        return self._conn

    def close(self):
        """Close connection if open."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
            self._pid = None


def sqlite_retry(
    max_attempts: int = 10,
    base_delay: float = 0.05,
    max_delay: float = 10.0,
    exceptions: tuple = (sqlite3.OperationalError,),
) -> Callable:
    """Decorator for SQLite operations with exponential backoff retry.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Check if it's a locking error
                    if "locked" not in str(e).lower() and attempt == 0:
                        # Not a lock error, don't retry
                        raise

                    if attempt < max_attempts - 1:
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (2**attempt), max_delay)

                        # Add jitter to prevent thundering herd
                        delay *= 0.5 + random.random()

                        time.sleep(delay)
                    else:
                        # Final attempt failed
                        raise last_exception from None

            # Should never reach here
            raise last_exception

        return wrapper

    return decorator


class ConnectionPool:
    """Simple connection pool for read-only connections."""

    def __init__(self, db_path: Path, pool_size: int = 5):
        """Initialize read-only connection pool.

        Args:
            db_path: Path to SQLite database
            pool_size: Number of connections to maintain
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._connections: list[sqlite3.Connection] = []
        self._available: list[bool] = []
        self._init_pool()

    def _init_pool(self):
        """Initialize connection pool with read-only connections."""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(
                f"file:{self.db_path}?mode=ro",
                uri=True,
                timeout=10.0,  # Read-only mode
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA query_only = ON")

            self._connections.append(conn)
            self._available.append(True)

    def get_connection(self) -> sqlite3.Connection | None:
        """Get available connection from pool."""
        for i, available in enumerate(self._available):
            if available:
                self._available[i] = False
                return self._connections[i]
        return None

    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool."""
        try:
            idx = self._connections.index(conn)
            self._available[idx] = True
        except ValueError:
            pass  # Connection not from this pool

    def close_all(self):
        """Close all connections in pool."""
        for conn in self._connections:
            try:
                conn.close()
            except Exception:
                pass
        self._connections.clear()
        self._available.clear()
