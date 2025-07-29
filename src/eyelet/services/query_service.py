"""Query service for retrieving and analyzing hook logs."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from eyelet.domain.config import LogFormat, LogScope
from eyelet.services.config_service import ConfigService
from eyelet.services.sqlite_connection import ProcessLocalConnection


@dataclass
class QueryFilter:
    """Filter criteria for querying logs."""

    hook_type: str | None = None
    tool_name: str | None = None
    session_id: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    status: str | None = None
    git_branch: str | None = None
    has_error: bool | None = None
    limit: int = 100
    offset: int = 0


class QueryService:
    """Service for querying hook logs from SQLite and JSON files."""

    def __init__(self, config_service: ConfigService):
        """Initialize query service.

        Args:
            config_service: Configuration service instance
        """
        self.config_service = config_service
        self.config = config_service.get_config()
        self._connections: dict[str, ProcessLocalConnection] = {}

    def _get_connection(self, db_path: Path) -> ProcessLocalConnection:
        """Get or create connection for database path."""
        path_str = str(db_path)
        if path_str not in self._connections:
            self._connections[path_str] = ProcessLocalConnection(db_path)
        return self._connections[path_str]

    def query(self, filter: QueryFilter) -> list[dict[str, Any]]:
        """Query logs based on filter criteria.

        Args:
            filter: Query filter criteria

        Returns:
            List of matching log entries
        """
        results = []

        # Determine which databases to query based on scope
        paths = self.config_service.get_effective_logging_paths()

        if self.config.logging.scope in [LogScope.PROJECT, LogScope.BOTH]:
            if self.config.logging.format in [LogFormat.SQLITE, LogFormat.BOTH]:
                project_results = self._query_sqlite(
                    paths["project"] / "eyelet.db", filter
                )
                results.extend(project_results)

        if self.config.logging.scope in [LogScope.GLOBAL, LogScope.BOTH]:
            if self.config.logging.format in [LogFormat.SQLITE, LogFormat.BOTH]:
                global_results = self._query_sqlite(
                    paths["global"] / "eyelet.db", filter
                )
                results.extend(global_results)

        # Sort by timestamp descending
        results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

        # Apply offset and limit
        if filter.offset > 0:
            results = results[filter.offset :]
        if filter.limit > 0:
            results = results[: filter.limit]

        return results

    def _query_sqlite(self, db_path: Path, filter: QueryFilter) -> list[dict[str, Any]]:
        """Query SQLite database."""
        if not db_path.exists():
            return []

        conn_manager = self._get_connection(db_path)
        conn = conn_manager.connection

        # Build WHERE clause
        conditions = []
        params = []

        if filter.hook_type:
            conditions.append("hook_type = ?")
            params.append(filter.hook_type)

        if filter.tool_name:
            conditions.append("tool_name = ?")
            params.append(filter.tool_name)

        if filter.session_id:
            conditions.append("session_id = ?")
            params.append(filter.session_id)

        if filter.since:
            conditions.append("timestamp >= ?")
            params.append(filter.since.timestamp())

        if filter.until:
            conditions.append("timestamp <= ?")
            params.append(filter.until.timestamp())

        if filter.status:
            conditions.append("status = ?")
            params.append(filter.status)

        if filter.git_branch:
            conditions.append("git_branch = ?")
            params.append(filter.git_branch)

        if filter.has_error is not None:
            if filter.has_error:
                conditions.append("error_code IS NOT NULL")
            else:
                conditions.append("error_code IS NULL")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Build query
        sql = f"""
        SELECT
            id, timestamp, timestamp_iso, session_id, hook_type,
            tool_name, status, duration_ms, hostname, ip_address,
            project_dir, git_branch, error_code, data
        FROM hooks
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        """

        params.extend([filter.limit, filter.offset])

        # Execute query
        cursor = conn.execute(sql, params)
        results = []

        for row in cursor:
            # Parse JSON data
            data = json.loads(row["data"])

            # Add database fields
            data["_id"] = row["id"]
            data["_source"] = "sqlite"
            data["_db_path"] = str(db_path)

            results.append(data)

        return results

    def get_summary(self, since: datetime | None = None) -> dict[str, Any]:
        """Get summary statistics of hooks.

        Args:
            since: Start time for statistics (default: last 24 hours)

        Returns:
            Summary statistics
        """
        if since is None:
            since = datetime.now() - timedelta(days=1)

        stats = {
            "period_start": since.isoformat(),
            "period_end": datetime.now().isoformat(),
            "total_hooks": 0,
            "by_type": {},
            "by_tool": {},
            "by_status": {},
            "sessions": set(),
            "errors": 0,
            "avg_duration_ms": 0,
        }

        # Query all sources
        filter = QueryFilter(since=since, limit=10000)
        results = self.query(filter)

        total_duration = 0
        duration_count = 0

        for result in results:
            stats["total_hooks"] += 1

            # Count by type
            hook_type = result.get("hook_type", "unknown")
            stats["by_type"][hook_type] = stats["by_type"].get(hook_type, 0) + 1

            # Count by tool
            tool_name = result.get("tool_name")
            if tool_name:
                stats["by_tool"][tool_name] = stats["by_tool"].get(tool_name, 0) + 1

            # Count by status
            execution = result.get("execution") or {}
            status = execution.get("status", "unknown") if execution else "unknown"
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Track sessions
            session_id = result.get("session_id")
            if session_id:
                stats["sessions"].add(session_id)

            # Count errors
            if execution and execution.get("error_message"):
                stats["errors"] += 1

            # Track duration
            duration = execution.get("duration_ms") if execution else None
            if duration:
                total_duration += duration
                duration_count += 1

        # Calculate averages
        stats["unique_sessions"] = len(stats["sessions"])
        del stats["sessions"]  # Remove set from JSON serializable output

        if duration_count > 0:
            stats["avg_duration_ms"] = round(total_duration / duration_count, 2)

        return stats

    def get_recent_errors(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent hooks with errors.

        Args:
            limit: Maximum number of results

        Returns:
            List of hooks with errors
        """
        filter = QueryFilter(has_error=True, limit=limit)
        return self.query(filter)

    def get_session_timeline(self, session_id: str) -> list[dict[str, Any]]:
        """Get all hooks for a specific session in chronological order.

        Args:
            session_id: Session ID to query

        Returns:
            List of hooks in chronological order
        """
        filter = QueryFilter(session_id=session_id, limit=10000)
        results = self.query(filter)

        # Sort by timestamp ascending for timeline
        results.sort(key=lambda x: x.get("timestamp_unix", 0))

        return results

    def search_logs(self, search_term: str, limit: int = 100) -> list[dict[str, Any]]:
        """Search logs for a specific term in the data.

        Args:
            search_term: Term to search for
            limit: Maximum results

        Returns:
            List of matching logs
        """
        # This is a simple implementation - could be enhanced with full-text search
        results = []

        # Query all recent logs
        filter = QueryFilter(limit=1000)
        all_logs = self.query(filter)

        # Search through JSON data
        for log in all_logs:
            log_str = json.dumps(log).lower()
            if search_term.lower() in log_str:
                results.append(log)
                if len(results) >= limit:
                    break

        return results
