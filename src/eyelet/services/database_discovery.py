"""Database discovery service for finding eyelet databases across the system."""

import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class DatabaseDiscoveryService:
    """Service for discovering eyelet databases across the filesystem."""
    
    def __init__(self):
        """Initialize database discovery service."""
        self.platform = platform.system().lower()
        self._known_locations: List[Path] = []
        
    def find_databases(self, use_cache: bool = True) -> List[Path]:
        """Find all eyelet databases on the system.
        
        Args:
            use_cache: Whether to include previously found locations
            
        Returns:
            List of paths to eyelet.db files
        """
        databases = []
        
        # Start with cached known locations if requested
        if use_cache:
            databases.extend(self._validate_known_locations())
        
        # Discover new databases
        discovered = self._discover_databases()
        
        # Merge and deduplicate
        all_paths = set(databases + discovered)
        
        # Update known locations cache
        self._known_locations = list(all_paths)
        
        # Sort by modification time (most recent first)
        valid_paths = [p for p in all_paths if p.exists()]
        valid_paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        return valid_paths
    
    def _discover_databases(self) -> List[Path]:
        """Discover databases using platform-specific methods."""
        if self.platform == "darwin":  # macOS
            return self._discover_macos()
        elif self.platform == "linux":
            return self._discover_linux()
        elif self.platform == "windows":
            return self._discover_windows()
        else:
            return self._discover_fallback()
    
    def _discover_macos(self) -> List[Path]:
        """Discover databases on macOS using mdfind."""
        databases = []
        
        try:
            # Try mdfind with proper filename metadata search
            result = subprocess.run([
                "mdfind", "kMDItemDisplayName == 'eyelet.db'"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    if line and line.endswith('eyelet.db'):
                        path = Path(line)
                        if path.exists() and path.is_file():
                            databases.append(path)
            
            # If that didn't work, try searching for SQLite files named eyelet.db
            if not databases:
                result2 = subprocess.run([
                    "mdfind", "kMDItemKind == 'SQLite Database' AND kMDItemDisplayName == 'eyelet.db'"
                ], capture_output=True, text=True, timeout=10)
                
                if result2.returncode == 0 and result2.stdout.strip():
                    for line in result2.stdout.strip().split('\n'):
                        if line and line.endswith('eyelet.db'):
                            path = Path(line)
                            if path.exists() and path.is_file():
                                databases.append(path)
            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass  # Will fall through to fallback
        
        # Always also try fallback method to ensure we don't miss any
        fallback_databases = self._discover_fallback()
        
        # Combine and deduplicate
        all_databases = set(databases + fallback_databases)
        return list(all_databases)
    
    def _discover_linux(self) -> List[Path]:
        """Discover databases on Linux using find or fd."""
        databases = []
        
        # Try fd first (faster)
        if self._command_exists("fd"):
            try:
                result = subprocess.run([
                    "fd", "-t", "f", "-H", "eyelet.db", str(Path.home())
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            path = Path(line)
                            if path.exists() and path.is_file():
                                databases.append(path)
                    return databases
                    
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass
        
        # Fallback to find command
        try:
            result = subprocess.run([
                "find", str(Path.home()), "-name", "eyelet.db", "-type", "f"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        path = Path(line)
                        if path.exists() and path.is_file():
                            databases.append(path)
                            
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            # Final fallback to manual search
            databases.extend(self._discover_fallback())
        
        return databases
    
    def _discover_windows(self) -> List[Path]:
        """Discover databases on Windows using where or fallback."""
        databases = []
        
        # Try using PowerShell Get-ChildItem for fast search
        try:
            powershell_cmd = [
                "powershell", "-Command",
                f"Get-ChildItem -Path '{Path.home()}' -Recurse -Name 'eyelet.db' -File -ErrorAction SilentlyContinue | ForEach-Object {{ Join-Path '{Path.home()}' $_ }}"
            ]
            
            result = subprocess.run(
                powershell_cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        path = Path(line)
                        if path.exists() and path.is_file():
                            databases.append(path)
                return databases
                
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass
        
        # Fallback to manual search
        return self._discover_fallback()
    
    def _discover_fallback(self) -> List[Path]:
        """Fallback discovery using manual filesystem traversal."""
        databases = []
        search_paths = self._get_common_search_paths()
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            try:
                # Search recursively but limit depth to avoid performance issues
                databases.extend(self._search_directory(search_path, max_depth=6))
            except (PermissionError, OSError):
                # Skip directories we can't access
                continue
        
        return databases
    
    def _search_directory(self, directory: Path, max_depth: int) -> List[Path]:
        """Recursively search directory for eyelet.db files."""
        if max_depth <= 0:
            return []
        
        databases = []
        
        try:
            for item in directory.iterdir():
                if item.is_file() and item.name == "eyelet.db":
                    databases.append(item)
                elif item.is_dir() and self._should_search_directory(item.name):
                    # Recurse into subdirectories (skip most hidden ones except eyelet-related)
                    databases.extend(self._search_directory(item, max_depth - 1))
                    
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        return databases
    
    def _should_search_directory(self, dir_name: str) -> bool:
        """Determine if a directory should be searched for databases.
        
        Args:
            dir_name: Directory name to check
            
        Returns:
            True if directory should be searched
        """
        # Don't search hidden directories except for eyelet-related ones
        if dir_name.startswith('.'):
            eyelet_related = [
                '.eyelet', 
                '.eyelet-logs', 
                '.eyelet-logging',
                '.claude'  # Claude directories may contain eyelet databases
            ]
            return dir_name in eyelet_related
        
        # Search all non-hidden directories
        return True
    
    def _get_common_search_paths(self) -> List[Path]:
        """Get common paths where eyelet databases might be located."""
        home = Path.home()
        paths = [
            home / ".eyelet",
            home / ".claude",
            home / "src",
            home / "dev",
            home / "projects",
            home / "code",
            home / "Documents",
        ]
        
        # Add specific patterns we know about
        known_patterns = [
            ".eyelet-logs",
            ".eyelet-logging", 
            ".claude/eyelet-logging",
        ]
        
        # Add project directories under src/
        src_dir = home / "src"
        if src_dir.exists():
            try:
                # Look for common project directory patterns
                for item in src_dir.iterdir():
                    if item.is_dir():
                        paths.append(item)
                        # Also check subdirectories for nested projects
                        try:
                            for subitem in item.iterdir():
                                if subitem.is_dir():
                                    paths.append(subitem)
                        except (PermissionError, OSError):
                            pass
            except (PermissionError, OSError):
                pass
        
        return paths
    
    def _validate_known_locations(self) -> List[Path]:
        """Validate and return existing known database locations."""
        valid = []
        for path in self._known_locations:
            if path.exists() and path.is_file():
                valid.append(path)
        return valid
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            result = subprocess.run(
                ["which", command] if self.platform != "windows" else ["where", command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def add_known_location(self, path: Path) -> None:
        """Add a known database location to the cache.
        
        Args:
            path: Path to an eyelet database
        """
        if path.exists() and path.is_file() and path not in self._known_locations:
            self._known_locations.append(path)
    
    def remove_known_location(self, path: Path) -> None:
        """Remove a known database location from the cache.
        
        Args:
            path: Path to remove from cache
        """
        if path in self._known_locations:
            self._known_locations.remove(path)
    
    def get_known_locations(self) -> List[Path]:
        """Get all known database locations.
        
        Returns:
            List of known database paths
        """
        return self._known_locations.copy()
    
    def find_project_databases(self, project_path: Path) -> List[Path]:
        """Find databases within a specific project directory.
        
        Args:
            project_path: Root path of the project to search
            
        Returns:
            List of eyelet databases found in the project
        """
        if not project_path.exists() or not project_path.is_dir():
            return []
        
        databases = []
        
        # Look for common eyelet database locations within the project
        common_names = [
            ".eyelet/eyelet.db",
            ".eyelet-logs/eyelet.db", 
            ".eyelet-logging/eyelet.db",
            "eyelet.db"
        ]
        
        for name in common_names:
            db_path = project_path / name
            if db_path.exists() and db_path.is_file():
                databases.append(db_path)
        
        # Also do a limited recursive search
        databases.extend(self._search_directory(project_path, max_depth=3))
        
        # Remove duplicates and sort
        unique_databases = list(set(databases))
        unique_databases.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        return unique_databases