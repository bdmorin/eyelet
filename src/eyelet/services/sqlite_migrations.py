"""SQLite schema migration system for Eyelet."""

from pathlib import Path

from eyelet.services.sqlite_connection import ProcessLocalConnection, sqlite_retry

# Import conversation migrations
from eyelet.recall.migrations import CONVERSATION_SCHEMA_V1

# Migration format: (version, description, SQL)
MIGRATIONS: list[tuple[int, str, str]] = [
    (
        1,
        "Initial schema",
        """
        -- Initial schema is handled by SQLiteLogger.SCHEMA
        -- This migration is a placeholder
    """,
    ),
    # Conversation search feature
    (2, "Add conversation search tables", CONVERSATION_SCHEMA_V1),
    # Future migrations will be added here
    # (3, "Add user_id column", """
    #     ALTER TABLE hooks ADD COLUMN user_id TEXT;
    #     CREATE INDEX idx_user_id ON hooks(user_id);
    # """),
]


class MigrationManager:
    """Manages SQLite schema migrations using PRAGMA user_version."""

    def __init__(self, db_path: Path):
        """Initialize migration manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._conn_manager = ProcessLocalConnection(db_path)

    def get_current_version(self) -> int:
        """Get current schema version from database."""
        conn = self._conn_manager.connection
        result = conn.execute("PRAGMA user_version").fetchone()
        return result[0] if result else 0

    def set_version(self, version: int):
        """Set schema version in database."""
        conn = self._conn_manager.connection
        conn.execute(f"PRAGMA user_version = {version}")

    @sqlite_retry(max_attempts=5)
    def migrate(self) -> list[str]:
        """Run pending migrations.

        Returns:
            List of migration descriptions that were applied
        """
        current_version = self.get_current_version()
        applied = []

        conn = self._conn_manager.connection

        for version, description, sql in MIGRATIONS:
            if version > current_version:
                try:
                    # Execute migration SQL
                    if sql.strip():  # Skip empty migrations
                        # Use executescript which handles its own transactions
                        conn.executescript(sql)

                    # Update version (autocommit mode, so this is immediate)
                    self.set_version(version)

                    applied.append(f"v{version}: {description}")

                except Exception as e:
                    raise RuntimeError(f"Migration {version} failed: {e}") from e

        return applied

    def needs_migration(self) -> bool:
        """Check if database needs migration."""
        current_version = self.get_current_version()
        latest_version = MIGRATIONS[-1][0] if MIGRATIONS else 0
        return current_version < latest_version

    def get_pending_migrations(self) -> list[tuple[int, str]]:
        """Get list of pending migrations.

        Returns:
            List of (version, description) tuples
        """
        current_version = self.get_current_version()
        pending = []

        for version, description, _ in MIGRATIONS:
            if version > current_version:
                pending.append((version, description))

        return pending
