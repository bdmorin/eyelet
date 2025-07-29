"""Configuration domain models for Eyelet."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class LogFormat(str, Enum):
    """Supported logging formats."""

    JSON = "json"
    SQLITE = "sqlite"
    BOTH = "both"


class LogScope(str, Enum):
    """Logging scope options."""

    PROJECT = "project"
    GLOBAL = "global"
    BOTH = "both"


class MetadataConfig(BaseModel):
    """Metadata configuration."""

    include_hostname: bool = True
    include_ip: bool = True
    custom_fields: dict[str, Any] = Field(default_factory=dict)


class LoggingConfig(BaseModel):
    """Logging configuration."""

    format: LogFormat = LogFormat.JSON
    enabled: bool = True
    scope: LogScope = LogScope.PROJECT
    global_path: str = "~/.claude/eyelet-logging"
    project_path: str = ".eyelet-logging"
    path: str | None = None  # Override for project-specific path
    add_to_gitignore: bool = True


class EyeletConfig(BaseModel):
    """Main Eyelet configuration."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    metadata: MetadataConfig = Field(default_factory=MetadataConfig)

    @classmethod
    def default(cls) -> "EyeletConfig":
        """Create default configuration."""
        return cls()

    def merge_with(self, other: "EyeletConfig") -> "EyeletConfig":
        """Merge this config with another, with other taking precedence."""
        # Deep merge logic
        merged_dict = self.model_dump()
        other_dict = other.model_dump()

        # Recursive merge helper
        def deep_merge(base: dict, override: dict) -> dict:
            result = base.copy()
            for key, value in override.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged = deep_merge(merged_dict, other_dict)
        return EyeletConfig(**merged)
