"""SQLite performance monitoring and statistics."""

import time
from dataclasses import dataclass, field
from datetime import datetime

from eyelet.services.sqlite_connection import ProcessLocalConnection


@dataclass
class PerformanceStats:
    """Track performance statistics for SQLite operations."""

    total_inserts: int = 0
    failed_inserts: int = 0
    total_queries: int = 0
    retry_count: int = 0

    # Timing statistics (in seconds)
    insert_times: list[float] = field(default_factory=list)
    query_times: list[float] = field(default_factory=list)

    # Lock wait times
    lock_wait_times: list[float] = field(default_factory=list)

    def add_insert(self, duration: float, retries: int = 0):
        """Record an insert operation."""
        self.total_inserts += 1
        self.insert_times.append(duration)
        self.retry_count += retries

    def add_failed_insert(self):
        """Record a failed insert."""
        self.failed_inserts += 1

    def add_query(self, duration: float):
        """Record a query operation."""
        self.total_queries += 1
        self.query_times.append(duration)

    def add_lock_wait(self, duration: float):
        """Record time spent waiting for locks."""
        self.lock_wait_times.append(duration)

    @property
    def avg_insert_time(self) -> float:
        """Average insert time in milliseconds."""
        if not self.insert_times:
            return 0.0
        return sum(self.insert_times) / len(self.insert_times) * 1000

    @property
    def avg_query_time(self) -> float:
        """Average query time in milliseconds."""
        if not self.query_times:
            return 0.0
        return sum(self.query_times) / len(self.query_times) * 1000

    @property
    def success_rate(self) -> float:
        """Insert success rate as percentage."""
        total = self.total_inserts + self.failed_inserts
        if total == 0:
            return 100.0
        return (self.total_inserts / total) * 100

    def get_summary(self) -> dict[str, any]:
        """Get performance summary."""
        return {
            "total_inserts": self.total_inserts,
            "failed_inserts": self.failed_inserts,
            "success_rate": f"{self.success_rate:.1f}%",
            "avg_insert_ms": f"{self.avg_insert_time:.2f}",
            "avg_query_ms": f"{self.avg_query_time:.2f}",
            "total_retries": self.retry_count,
            "lock_waits": len(self.lock_wait_times),
            "avg_lock_wait_ms": (
                f"{sum(self.lock_wait_times) * 1000 / len(self.lock_wait_times):.2f}"
                if self.lock_wait_times
                else "0.00"
            ),
        }


class SQLiteMonitor:
    """Monitor SQLite database health and performance."""

    def __init__(self, db_path):
        """Initialize monitor.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._conn_manager = ProcessLocalConnection(db_path)
        self.stats = PerformanceStats()

    def get_database_stats(self) -> dict[str, any]:
        """Get database statistics and health metrics."""
        conn = self._conn_manager.connection

        stats = {}

        # Database size
        stats["size_mb"] = self.db_path.stat().st_size / (1024 * 1024)

        # Table statistics
        table_info = conn.execute(
            """
            SELECT COUNT(*) as total_rows,
                   COUNT(DISTINCT session_id) as unique_sessions,
                   COUNT(DISTINCT hook_type) as hook_types,
                   MIN(timestamp) as oldest_record,
                   MAX(timestamp) as newest_record
            FROM hooks
        """
        ).fetchone()

        stats["total_rows"] = table_info[0]
        stats["unique_sessions"] = table_info[1]
        stats["hook_types"] = table_info[2]

        if table_info[3]:
            oldest = datetime.fromtimestamp(table_info[3])
            newest = datetime.fromtimestamp(table_info[4])
            stats["oldest_record"] = oldest.isoformat()
            stats["newest_record"] = newest.isoformat()
            stats["time_span_days"] = (newest - oldest).days

        # WAL mode status
        wal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        stats["wal_mode"] = wal_mode == "wal"

        # Cache statistics
        cache_stats = conn.execute("PRAGMA cache_stats").fetchone()
        if cache_stats:
            stats["cache_hit_rate"] = (
                f"{(cache_stats[0] / (cache_stats[0] + cache_stats[1]) * 100):.1f}%"
            )

        # Index usage (check if our indexes are being used)
        stats["indexes"] = []
        for row in conn.execute("PRAGMA index_list(hooks)"):
            index_name = row[1]
            index_info = conn.execute(f"PRAGMA index_info({index_name})").fetchall()
            stats["indexes"].append(
                {"name": index_name, "columns": [col[2] for col in index_info]}
            )

        return stats

    def get_recent_activity(self, minutes: int = 5) -> dict[str, any]:
        """Get activity statistics for recent time period."""
        conn = self._conn_manager.connection

        since = time.time() - (minutes * 60)

        # Recent activity by hook type
        activity = conn.execute(
            """
            SELECT hook_type, COUNT(*) as count,
                   AVG(duration_ms) as avg_duration
            FROM hooks
            WHERE timestamp > ?
            GROUP BY hook_type
            ORDER BY count DESC
        """,
            (since,),
        ).fetchall()

        return {
            "period_minutes": minutes,
            "activity_by_type": [
                {
                    "hook_type": row[0],
                    "count": row[1],
                    "avg_duration_ms": f"{row[2]:.2f}" if row[2] else "N/A",
                }
                for row in activity
            ],
        }

    def check_health(self) -> dict[str, any]:
        """Perform health checks on the database."""
        conn = self._conn_manager.connection

        health = {"status": "healthy", "issues": []}

        # Check integrity
        try:
            result = conn.execute("PRAGMA integrity_check").fetchone()
            if result[0] != "ok":
                health["status"] = "unhealthy"
                health["issues"].append(f"Integrity check failed: {result[0]}")
        except Exception as e:
            health["status"] = "unhealthy"
            health["issues"].append(f"Integrity check error: {e}")

        # Check WAL size (should checkpoint if too large)
        if self.db_path.with_suffix(".db-wal").exists():
            wal_size = self.db_path.with_suffix(".db-wal").stat().st_size / (
                1024 * 1024
            )
            if wal_size > 100:  # 100MB threshold
                health["issues"].append(
                    f"WAL file large ({wal_size:.1f}MB), consider checkpoint"
                )

        # Check database size
        db_size = self.db_path.stat().st_size / (1024 * 1024)
        if db_size > 1000:  # 1GB threshold
            health["issues"].append(
                f"Database size large ({db_size:.1f}MB), consider cleanup"
            )

        # Check for long-running transactions
        active_txns = conn.execute("PRAGMA lock_status").fetchall()
        if active_txns:
            health["issues"].append(f"Active transactions detected: {len(active_txns)}")

        if health["issues"] and health["status"] == "healthy":
            health["status"] = "warning"

        return health

    def optimize_database(self):
        """Run optimization commands on the database."""
        conn = self._conn_manager.connection

        optimizations = []

        # Checkpoint WAL file
        result = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        optimizations.append(f"WAL checkpoint: {result[0]} pages moved")

        # Analyze tables for query optimizer
        conn.execute("ANALYZE")
        optimizations.append("Table statistics updated")

        # Vacuum if needed (this can be slow for large databases)
        if self.db_path.stat().st_size > 100 * 1024 * 1024:  # 100MB
            # Just suggest vacuum instead of running it
            optimizations.append("VACUUM recommended for space reclamation")

        return optimizations
