"""Unified hook logging service supporting JSON files and SQLite."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from eyelet.domain.config import LogFormat, LogScope
from eyelet.domain.hooks import HookData
from eyelet.services.config_service import ConfigService
from eyelet.services.git_metadata import GitMetadata
from eyelet.services.sqlite_logger import SQLiteLogger


class HookLogger:
    """Unified logger that handles both JSON file and SQLite logging."""

    def __init__(self, config_service: ConfigService, project_dir: Path | None = None):
        """Initialize hook logger.

        Args:
            config_service: Configuration service instance
            project_dir: Project directory for context
        """
        self.config_service = config_service
        self.config = config_service.get_config()
        self._sqlite_loggers: dict[str, SQLiteLogger] = {}
        self._git_metadata = GitMetadata(project_dir)

    def _get_sqlite_logger(self, path: Path) -> SQLiteLogger:
        """Get or create SQLite logger for path."""
        path_str = str(path)
        if path_str not in self._sqlite_loggers:
            db_path = path / "eyelet.db"
            self._sqlite_loggers[path_str] = SQLiteLogger(db_path)
        return self._sqlite_loggers[path_str]

    def _create_hook_data(
        self, input_data: dict[str, Any], start_time: datetime
    ) -> HookData:
        """Create HookData object from raw input."""
        # Extract core fields
        hook_type = input_data.get("hook_event_name", "unknown")
        tool_name = input_data.get("tool_name", "")
        session_id = input_data.get("session_id", "unknown")

        # Build HookData
        hook_data = HookData(
            timestamp=start_time.isoformat(),
            timestamp_unix=start_time.timestamp(),
            hook_type=hook_type,
            tool_name=tool_name,
            session_id=session_id,
            transcript_path=input_data.get("transcript_path", ""),
            cwd=Path(input_data.get("cwd", os.getcwd())),
            environment={
                "python_version": sys.version,
                "platform": sys.platform,
                "eyelet_version": "0.2.0",  # TODO: Import from __version__
                "env_vars": {
                    k: v
                    for k, v in os.environ.items()
                    if k.startswith(("CLAUDE", "EYELET", "ANTHROPIC"))
                },
            },
            input_data=input_data,
            metadata={},
        )

        # Add Git metadata if enabled
        if self.config.metadata.include_hostname or self.config.metadata.include_ip:
            # Add system metadata
            import socket

            if self.config.metadata.include_hostname:
                try:
                    hook_data.metadata["hostname"] = socket.gethostname()
                except Exception:
                    pass

            if self.config.metadata.include_ip:
                try:
                    hostname = socket.gethostname()
                    hook_data.metadata["ip_address"] = socket.gethostbyname(hostname)
                except Exception:
                    pass

        # Add Git metadata
        git_info = self._git_metadata.get_metadata()
        if git_info:
            hook_data.metadata["git"] = git_info

        # Add custom fields from config
        if self.config.metadata.custom_fields:
            hook_data.metadata.update(self.config.metadata.custom_fields)

        return hook_data

    def _log_to_json_file(self, hook_data: HookData, log_dir: Path) -> Path:
        """Log hook data to JSON file.

        Args:
            hook_data: Hook data to log
            log_dir: Directory to log to

        Returns:
            Path to created log file
        """
        # Build directory structure
        if hook_data.hook_type in ["PreToolUse", "PostToolUse"] and hook_data.tool_name:
            dir_path = (
                log_dir
                / hook_data.hook_type
                / hook_data.tool_name
                / datetime.now().strftime("%Y-%m-%d")
            )
        elif hook_data.hook_type == "PreCompact":
            compact_type = hook_data.input_data.get("compact_type", "unknown")
            dir_path = (
                log_dir
                / hook_data.hook_type
                / compact_type
                / datetime.now().strftime("%Y-%m-%d")
            )
        else:
            dir_path = (
                log_dir / hook_data.hook_type / datetime.now().strftime("%Y-%m-%d")
            )

        # Create directory
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create filename
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        if hook_data.tool_name:
            filename = (
                f"{timestamp_str}_{hook_data.hook_type}_{hook_data.tool_name}.json"
            )
        else:
            filename = f"{timestamp_str}_{hook_data.hook_type}.json"

        log_file = dir_path / filename

        # Add file metadata
        hook_data.metadata.update(
            {
                "log_file": str(log_file),
                "log_dir": str(dir_path),
                "project_dir": str(hook_data.cwd),
            }
        )

        # Write log file
        with open(log_file, "w") as f:
            json.dump(hook_data.model_dump(), f, indent=2, default=str)

        return log_file

    def log_hook(
        self, input_data: dict[str, Any], start_time: datetime | None = None
    ) -> dict[str, Any]:
        """Log hook data according to configuration.

        Args:
            input_data: Raw hook input data
            start_time: Start time (defaults to now)

        Returns:
            Dictionary with logging results
        """
        if not self.config.logging.enabled:
            return {"status": "disabled"}

        if start_time is None:
            start_time = datetime.now()

        # Create hook data
        hook_data = self._create_hook_data(input_data, start_time)

        # Store for potential updates
        self._last_hook_data = hook_data

        # Get logging paths
        paths = self.config_service.get_effective_logging_paths()
        results = {"status": "success", "logs": []}

        # Determine where to log based on scope
        log_locations = []
        if self.config.logging.scope in [LogScope.PROJECT, LogScope.BOTH]:
            log_locations.append(("project", paths["project"]))
        if self.config.logging.scope in [LogScope.GLOBAL, LogScope.BOTH]:
            log_locations.append(("global", paths["global"]))

        # Log to each location
        for location_type, path in log_locations:
            if self.config.logging.format in [LogFormat.JSON, LogFormat.BOTH]:
                # JSON file logging
                json_dir = path if path.name != "eyelet.db" else path.parent
                log_file = self._log_to_json_file(hook_data, json_dir)
                results["logs"].append(
                    {"type": "json", "location": location_type, "path": str(log_file)}
                )

            if self.config.logging.format in [LogFormat.SQLITE, LogFormat.BOTH]:
                # SQLite logging
                sqlite_logger = self._get_sqlite_logger(path)
                success = sqlite_logger.log_hook(hook_data)
                results["logs"].append(
                    {
                        "type": "sqlite",
                        "location": location_type,
                        "path": str(path / "eyelet.db"),
                        "success": success,
                    }
                )

        return results

    def update_hook_result(
        self,
        hook_data: HookData,
        status: str,
        duration_ms: int,
        output_data: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        """Update hook with execution results.

        This is called after hook execution completes to add results.
        For JSON files, we re-read and update. For SQLite, this would
        be handled differently in a future implementation.
        """
        # Update hook data
        from eyelet.domain.hooks import ExecutionResult

        hook_data.execution = ExecutionResult(
            status=status,
            duration_ms=duration_ms,
            output_data=output_data or {},
            error_message=error_message,
        )
        hook_data.completed_at = datetime.now().isoformat()

        # If we logged to JSON files, update them
        if "log_file" in hook_data.metadata:
            try:
                log_file = Path(hook_data.metadata["log_file"])
                if log_file.exists():
                    with open(log_file, "w") as f:
                        json.dump(hook_data.model_dump(), f, indent=2, default=str)
            except Exception:
                pass  # Don't fail on update errors
