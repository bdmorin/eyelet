"""Metrics service for aggregating data from multiple eyelet databases."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from eyelet.services.database_discovery import DatabaseDiscoveryService


class ActivityLevel(Enum):
    """Database activity levels based on recency."""
    ACTIVE = "active"      # < 5 minutes
    RECENT = "recent"      # 5-60 minutes
    STALE = "stale"        # > 1 hour


class DatabaseSchema(Enum):
    """Known database schema versions."""
    LEGACY_EXECUTIONS = "legacy"  # executions table
    MODERN_HOOKS = "modern"       # hooks table
    UNKNOWN = "unknown"


@dataclass
class DatabaseMetrics:
    """Metrics for a single eyelet database."""
    path: Path
    exists: bool
    record_count: int
    last_activity: Optional[datetime]
    activity_level: ActivityLevel
    schema_version: DatabaseSchema
    recent_errors: int
    size_bytes: int
    sessions: List[str]
    hook_types: Dict[str, int]
    tools: Dict[str, int]
    error_rate: float


@dataclass
class HookRecord:
    """Individual hook record from database."""
    id: int
    timestamp: datetime
    hook_type: str
    tool_name: Optional[str]
    session_id: str
    status: Optional[str]
    duration_ms: Optional[int]
    error_message: Optional[str]
    data: Dict[str, Any]
    database_path: Path


@dataclass
class SystemMetrics:
    """Overall system metrics across all databases."""
    total_databases: int
    total_records: int
    active_databases: int
    total_errors: int
    unique_sessions: int
    databases: List[DatabaseMetrics]
    last_updated: datetime


class MetricsService:
    """Service for collecting and aggregating metrics from eyelet databases."""
    
    def __init__(self, custom_db_path: Optional[Path] = None):
        """Initialize metrics service.
        
        Args:
            custom_db_path: Optional custom database path for centralized logging
        """
        self.custom_db_path = custom_db_path
        self.discovery_service = DatabaseDiscoveryService()
        self._cache: Optional[SystemMetrics] = None
        self._cache_expiry: Optional[datetime] = None
        self._cache_duration = timedelta(seconds=30)
    
    def get_system_metrics(self, use_cache: bool = True) -> SystemMetrics:
        """Get system-wide metrics across all databases.
        
        Args:
            use_cache: Whether to use cached results if available
            
        Returns:
            System metrics with all database information
        """
        now = datetime.now()
        
        # Return cached results if valid
        if (use_cache and self._cache and self._cache_expiry and 
            now < self._cache_expiry):
            return self._cache
        
        # Use either custom database or discover all databases
        if self.custom_db_path:
            db_paths = [self.custom_db_path]
        else:
            db_paths = self.discovery_service.find_databases()
        databases = []
        
        total_records = 0
        total_errors = 0
        active_count = 0
        all_sessions = set()
        
        # Collect metrics for each database
        for db_path in db_paths:
            db_metrics = self._get_database_metrics(db_path)
            databases.append(db_metrics)
            
            if db_metrics.exists:
                total_records += db_metrics.record_count
                total_errors += db_metrics.recent_errors
                all_sessions.update(db_metrics.sessions)
                
                if db_metrics.activity_level == ActivityLevel.ACTIVE:
                    active_count += 1
        
        # Create system metrics
        system_metrics = SystemMetrics(
            total_databases=len(databases),
            total_records=total_records,
            active_databases=active_count,
            total_errors=total_errors,
            unique_sessions=len(all_sessions),
            databases=databases,
            last_updated=now
        )
        
        # Cache results
        self._cache = system_metrics
        self._cache_expiry = now + self._cache_duration
        
        return system_metrics
    
    def get_database_metrics(self, db_path: Path) -> DatabaseMetrics:
        """Get detailed metrics for a specific database.
        
        Args:
            db_path: Path to the eyelet database
            
        Returns:
            Database metrics
        """
        return self._get_database_metrics(db_path)
    
    def get_recent_hooks(self, db_path: Path, limit: int = 100) -> List[HookRecord]:
        """Get recent hooks from a specific database.
        
        Args:
            db_path: Path to the eyelet database
            limit: Maximum number of hooks to return
            
        Returns:
            List of recent hook records
        """
        if not db_path.exists():
            return []
        
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Detect schema and query accordingly
                schema = self._detect_schema(conn)
                
                if schema == DatabaseSchema.MODERN_HOOKS:
                    return self._get_hooks_modern_schema(conn, db_path, limit)
                elif schema == DatabaseSchema.LEGACY_EXECUTIONS:
                    return self._get_hooks_legacy_schema(conn, db_path, limit)
                else:
                    return []
                    
        except Exception:
            return []
    
    def search_hooks(self, query: str, limit: int = 100) -> List[HookRecord]:
        """Search for hooks across all databases.
        
        Args:
            query: Search term
            limit: Maximum results
            
        Returns:
            List of matching hook records
        """
        results = []
        db_paths = self.discovery_service.find_databases()
        
        for db_path in db_paths:
            if len(results) >= limit:
                break
                
            hooks = self.get_recent_hooks(db_path, limit - len(results))
            
            # Simple search through hook data
            for hook in hooks:
                if query.lower() in json.dumps(hook.data).lower():
                    results.append(hook)
        
        # Sort by timestamp descending
        results.sort(key=lambda h: h.timestamp, reverse=True)
        return results[:limit]
    
    def _get_database_metrics(self, db_path: Path) -> DatabaseMetrics:
        """Internal method to collect database metrics."""
        if not db_path.exists():
            return DatabaseMetrics(
                path=db_path,
                exists=False,
                record_count=0,
                last_activity=None,
                activity_level=ActivityLevel.STALE,
                schema_version=DatabaseSchema.UNKNOWN,
                recent_errors=0,
                size_bytes=0,
                sessions=[],
                hook_types={},
                tools={},
                error_rate=0.0
            )
        
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Detect schema
                schema = self._detect_schema(conn)
                
                # Get file size
                size_bytes = db_path.stat().st_size
                
                # Collect metrics based on schema
                if schema == DatabaseSchema.MODERN_HOOKS:
                    return self._collect_modern_metrics(conn, db_path, size_bytes)
                elif schema == DatabaseSchema.LEGACY_EXECUTIONS:
                    return self._collect_legacy_metrics(conn, db_path, size_bytes)
                else:
                    return self._empty_metrics(db_path, size_bytes, schema)
                    
        except Exception:
            return self._empty_metrics(db_path, 0, DatabaseSchema.UNKNOWN)
    
    def _detect_schema(self, conn: sqlite3.Connection) -> DatabaseSchema:
        """Detect database schema version."""
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'hooks' in tables:
            return DatabaseSchema.MODERN_HOOKS
        elif 'executions' in tables:
            return DatabaseSchema.LEGACY_EXECUTIONS
        else:
            return DatabaseSchema.UNKNOWN
    
    def _collect_modern_metrics(self, conn: sqlite3.Connection, db_path: Path, size_bytes: int) -> DatabaseMetrics:
        """Collect metrics from modern hooks table."""
        # Basic counts
        cursor = conn.execute("SELECT COUNT(*) FROM hooks")
        record_count = cursor.fetchone()[0]
        
        if record_count == 0:
            return self._empty_metrics(db_path, size_bytes, DatabaseSchema.MODERN_HOOKS)
        
        # Last activity
        cursor = conn.execute("SELECT MAX(timestamp) FROM hooks")
        last_timestamp = cursor.fetchone()[0]
        last_activity = datetime.fromtimestamp(last_timestamp) if last_timestamp else None
        
        # Activity level
        activity_level = self._calculate_activity_level(last_activity)
        
        # Recent errors (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM hooks WHERE error_code IS NOT NULL AND timestamp >= ?",
            (yesterday.timestamp(),)
        )
        recent_errors = cursor.fetchone()[0]
        
        # Sessions
        cursor = conn.execute("SELECT DISTINCT session_id FROM hooks ORDER BY timestamp DESC LIMIT 100")
        sessions = [row[0] for row in cursor.fetchall()]
        
        # Hook types
        cursor = conn.execute("SELECT hook_type, COUNT(*) FROM hooks GROUP BY hook_type")
        hook_types = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Tools
        cursor = conn.execute("SELECT tool_name, COUNT(*) FROM hooks WHERE tool_name IS NOT NULL GROUP BY tool_name")
        tools = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Error rate
        error_rate = (recent_errors / record_count * 100) if record_count > 0 else 0.0
        
        return DatabaseMetrics(
            path=db_path,
            exists=True,
            record_count=record_count,
            last_activity=last_activity,
            activity_level=activity_level,
            schema_version=DatabaseSchema.MODERN_HOOKS,
            recent_errors=recent_errors,
            size_bytes=size_bytes,
            sessions=sessions,
            hook_types=hook_types,
            tools=tools,
            error_rate=error_rate
        )
    
    def _collect_legacy_metrics(self, conn: sqlite3.Connection, db_path: Path, size_bytes: int) -> DatabaseMetrics:
        """Collect metrics from legacy executions table."""
        # Basic counts
        cursor = conn.execute("SELECT COUNT(*) FROM executions")
        record_count = cursor.fetchone()[0]
        
        if record_count == 0:
            return self._empty_metrics(db_path, size_bytes, DatabaseSchema.LEGACY_EXECUTIONS)
        
        # Last activity
        cursor = conn.execute("SELECT MAX(timestamp) FROM executions")
        last_timestamp = cursor.fetchone()[0]
        last_activity = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00')) if last_timestamp else None
        
        # Activity level
        activity_level = self._calculate_activity_level(last_activity)
        
        # Recent errors
        yesterday = datetime.now() - timedelta(days=1)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM executions WHERE error_message IS NOT NULL AND timestamp >= ?",
            (yesterday.isoformat(),)
        )
        recent_errors = cursor.fetchone()[0]
        
        # Hook types
        cursor = conn.execute("SELECT hook_type, COUNT(*) FROM executions GROUP BY hook_type")
        hook_types = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Tools
        cursor = conn.execute("SELECT tool_name, COUNT(*) FROM executions WHERE tool_name IS NOT NULL GROUP BY tool_name")
        tools = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Sessions (extract from hook_id if possible)
        sessions = []  # Legacy schema doesn't have session tracking
        
        # Error rate
        error_rate = (recent_errors / record_count * 100) if record_count > 0 else 0.0
        
        return DatabaseMetrics(
            path=db_path,
            exists=True,
            record_count=record_count,
            last_activity=last_activity,
            activity_level=activity_level,
            schema_version=DatabaseSchema.LEGACY_EXECUTIONS,
            recent_errors=recent_errors,
            size_bytes=size_bytes,
            sessions=sessions,
            hook_types=hook_types,
            tools=tools,
            error_rate=error_rate
        )
    
    def _get_hooks_modern_schema(self, conn: sqlite3.Connection, db_path: Path, limit: int) -> List[HookRecord]:
        """Get hooks from modern schema."""
        cursor = conn.execute("""
            SELECT id, timestamp, timestamp_iso, session_id, hook_type, tool_name, 
                   status, duration_ms, error_code, data
            FROM hooks 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        hooks = []
        for row in cursor.fetchall():
            hooks.append(HookRecord(
                id=row['id'],
                timestamp=datetime.fromtimestamp(row['timestamp']),
                hook_type=row['hook_type'],
                tool_name=row['tool_name'],
                session_id=row['session_id'],
                status=row['status'],
                duration_ms=row['duration_ms'],
                error_message=row['error_code'],
                data=json.loads(row['data']),
                database_path=db_path
            ))
        
        return hooks
    
    def _get_hooks_legacy_schema(self, conn: sqlite3.Connection, db_path: Path, limit: int) -> List[HookRecord]:
        """Get hooks from legacy schema."""
        cursor = conn.execute("""
            SELECT id, hook_id, hook_type, tool_name, timestamp, 
                   input_data, output_data, duration_ms, status, error_message
            FROM executions 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        hooks = []
        for row in cursor.fetchall():
            # Parse timestamp
            timestamp_str = row['timestamp']
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
            
            # Combine input/output data
            data = {}
            if row['input_data']:
                data.update(json.loads(row['input_data']))
            if row['output_data']:
                data['output'] = json.loads(row['output_data'])
            
            hooks.append(HookRecord(
                id=row['id'],
                timestamp=timestamp,
                hook_type=row['hook_type'],
                tool_name=row['tool_name'],
                session_id=row['hook_id'],  # Use hook_id as session
                status=row['status'],
                duration_ms=row['duration_ms'],
                error_message=row['error_message'],
                data=data,
                database_path=db_path
            ))
        
        return hooks
    
    def _calculate_activity_level(self, last_activity: Optional[datetime]) -> ActivityLevel:
        """Calculate activity level based on last activity time."""
        if not last_activity:
            return ActivityLevel.STALE
        
        now = datetime.now()
        delta = now - last_activity
        
        if delta < timedelta(minutes=5):
            return ActivityLevel.ACTIVE
        elif delta < timedelta(hours=1):
            return ActivityLevel.RECENT
        else:
            return ActivityLevel.STALE
    
    def _empty_metrics(self, db_path: Path, size_bytes: int, schema: DatabaseSchema) -> DatabaseMetrics:
        """Create empty metrics for databases with no data."""
        return DatabaseMetrics(
            path=db_path,
            exists=True,
            record_count=0,
            last_activity=None,
            activity_level=ActivityLevel.STALE,
            schema_version=schema,
            recent_errors=0,
            size_bytes=size_bytes,
            sessions=[],
            hook_types={},
            tools={},
            error_rate=0.0
        )
    
    def clear_cache(self) -> None:
        """Clear cached metrics to force refresh."""
        self._cache = None
        self._cache_expiry = None