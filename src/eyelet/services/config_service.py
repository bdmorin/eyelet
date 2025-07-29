"""Configuration management service for Eyelet."""

import os
from pathlib import Path
from typing import Any

import yaml

from eyelet.domain.config import EyeletConfig


class ConfigService:
    """Service for managing Eyelet configuration files."""

    GLOBAL_CONFIG_PATH = Path.home() / ".claude" / "eyelet.yaml"
    PROJECT_CONFIG_NAME = "eyelet.yaml"

    def __init__(self, project_dir: Path | None = None):
        """Initialize config service.

        Args:
            project_dir: Project directory path. If None, uses current directory.
        """
        self.project_dir = project_dir or Path.cwd()
        self._global_config: EyeletConfig | None = None
        self._project_config: EyeletConfig | None = None
        self._merged_config: EyeletConfig | None = None

    @property
    def project_config_path(self) -> Path:
        """Get project config file path."""
        return self.project_dir / self.PROJECT_CONFIG_NAME

    def load_global_config(self) -> EyeletConfig:
        """Load global configuration."""
        if self._global_config is None:
            if self.GLOBAL_CONFIG_PATH.exists():
                with open(self.GLOBAL_CONFIG_PATH) as f:
                    data = yaml.safe_load(f) or {}
                self._global_config = EyeletConfig(**data)
            else:
                self._global_config = EyeletConfig.default()
        return self._global_config

    def load_project_config(self) -> EyeletConfig | None:
        """Load project configuration if it exists."""
        if self._project_config is None and self.project_config_path.exists():
            with open(self.project_config_path) as f:
                data = yaml.safe_load(f) or {}
            self._project_config = EyeletConfig(**data)
        return self._project_config

    def get_config(self) -> EyeletConfig:
        """Get merged configuration (project overrides global)."""
        if self._merged_config is None:
            global_config = self.load_global_config()
            project_config = self.load_project_config()

            if project_config:
                self._merged_config = global_config.merge_with(project_config)
            else:
                self._merged_config = global_config

        return self._merged_config

    def save_global_config(self, config: EyeletConfig) -> None:
        """Save global configuration."""
        self.GLOBAL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(self.GLOBAL_CONFIG_PATH, "w") as f:
            # Convert to dict with mode='json' to ensure enums are serialized as strings
            data = config.model_dump(mode="json")
            yaml.dump(data, f, default_flow_style=False)
        self._global_config = config
        self._merged_config = None  # Reset cache

    def save_project_config(self, config: EyeletConfig) -> None:
        """Save project configuration."""
        with open(self.project_config_path, "w") as f:
            # Convert to dict with mode='json' to ensure enums are serialized as strings
            data = config.model_dump(mode="json")
            yaml.dump(data, f, default_flow_style=False)
        self._project_config = config
        self._merged_config = None  # Reset cache

    def update_config(self, updates: dict[str, Any], scope: str = "global") -> None:
        """Update configuration with dot notation support.

        Args:
            updates: Dictionary of updates (supports dot notation keys)
            scope: "global" or "project"
        """
        if scope == "global":
            config = self.load_global_config()
            save_func = self.save_global_config
        else:
            config = self.load_project_config() or EyeletConfig.default()
            save_func = self.save_project_config

        # Convert to dict for manipulation
        config_dict = config.model_dump()

        # Apply updates with dot notation support
        for key, value in updates.items():
            parts = key.split(".")
            current = config_dict

            # Navigate to the nested location
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the value
            current[parts[-1]] = value

        # Convert back to config object and save
        updated_config = EyeletConfig(**config_dict)
        save_func(updated_config)

    def get_effective_logging_paths(self) -> dict[str, Path]:
        """Get the effective logging paths based on configuration.

        Returns:
            Dictionary with 'global' and 'project' paths
        """
        config = self.get_config()
        paths = {}

        # Global path
        global_path = Path(os.path.expanduser(config.logging.global_path))
        paths["global"] = global_path

        # Project path
        if config.logging.path:
            # Use override if specified
            project_path = self.project_dir / config.logging.path
        else:
            project_path = self.project_dir / config.logging.project_path
        paths["project"] = project_path

        return paths
