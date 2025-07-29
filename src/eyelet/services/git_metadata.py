"""Git repository metadata collection for enriching logs."""

import subprocess
from pathlib import Path
from typing import Any


class GitMetadata:
    """Collect Git repository information for log enrichment."""

    def __init__(self, working_dir: Path | None = None):
        """Initialize Git metadata collector.

        Args:
            working_dir: Working directory to check for Git repo
        """
        self.working_dir = working_dir or Path.cwd()
        self._is_git_repo = self._check_git_repo()

    def _check_git_repo(self) -> bool:
        """Check if working directory is in a Git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=1,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _run_git_command(self, args: list[str]) -> str | None:
        """Run a Git command and return output."""
        if not self._is_git_repo:
            return None

        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return None

    def get_current_branch(self) -> str | None:
        """Get current Git branch name."""
        branch = self._run_git_command(["branch", "--show-current"])
        if not branch:
            # Try alternative method for detached HEAD
            branch = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        return branch

    def get_current_commit(self) -> str | None:
        """Get current commit hash (short form)."""
        return self._run_git_command(["rev-parse", "--short", "HEAD"])

    def get_remote_url(self) -> str | None:
        """Get remote repository URL."""
        url = self._run_git_command(["remote", "get-url", "origin"])
        if url:
            # Clean up URL for privacy (remove credentials)
            if "@" in url and ":" in url:
                # Handle git@github.com:user/repo.git format
                parts = url.split(":")
                if len(parts) == 2 and parts[0].endswith("github.com"):
                    return f"https://github.com/{parts[1]}"
            elif "https://" in url and "@" in url:
                # Handle https://user:token@github.com/user/repo.git format
                parts = url.split("@")
                if len(parts) == 2:
                    return f"https://{parts[1]}"
        return url

    def is_dirty(self) -> bool:
        """Check if working directory has uncommitted changes."""
        if not self._is_git_repo:
            return False

        status = self._run_git_command(["status", "--porcelain"])
        return bool(status)

    def get_repo_name(self) -> str | None:
        """Get repository name from remote URL."""
        url = self.get_remote_url()
        if url:
            # Extract repo name from URL
            if url.endswith(".git"):
                url = url[:-4]

            parts = url.split("/")
            if len(parts) >= 2:
                return parts[-1]

        # Fallback to directory name
        return self.working_dir.name

    def get_metadata(self) -> dict[str, Any]:
        """Get all Git metadata as a dictionary.

        Returns:
            Dictionary with Git information, empty if not a Git repo
        """
        if not self._is_git_repo:
            return {}

        metadata = {
            "is_git_repo": True,
            "branch": self.get_current_branch(),
            "commit": self.get_current_commit(),
            "dirty": self.is_dirty(),
            "repo_name": self.get_repo_name(),
        }

        # Only include remote URL if it's cleaned
        remote_url = self.get_remote_url()
        if remote_url and not any(
            sensitive in remote_url for sensitive in ["@", "token", "password"]
        ):
            metadata["remote_url"] = remote_url

        # Add user info if available
        user_name = self._run_git_command(["config", "user.name"])
        if user_name:
            metadata["user_name"] = user_name

        # Add last commit info
        last_commit_msg = self._run_git_command(["log", "-1", "--pretty=%s"])
        if last_commit_msg:
            metadata["last_commit_message"] = last_commit_msg[
                :100
            ]  # Truncate long messages

        # Filter out None values
        return {k: v for k, v in metadata.items() if v is not None}

    def clear_cache(self):
        """Clear cached Git information."""
        self.get_current_branch.cache_clear()
        self.get_current_commit.cache_clear()
        self.get_remote_url.cache_clear()
