"""Path utilities for eyelet with XDG Base Directory support."""

import os
from pathlib import Path
from typing import Optional


def get_xdg_data_home() -> Path:
    """Get XDG data directory for user data files.
    
    Returns XDG_DATA_HOME if set, otherwise ~/.local/share
    
    Returns:
        Path to XDG data directory
    """
    xdg_data_home = os.environ.get('XDG_DATA_HOME')
    if xdg_data_home:
        return Path(xdg_data_home)
    
    return Path.home() / '.local' / 'share'


def get_xdg_config_home() -> Path:
    """Get XDG config directory for configuration files.
    
    Returns XDG_CONFIG_HOME if set, otherwise ~/.config
    
    Returns:
        Path to XDG config directory
    """
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        return Path(xdg_config_home)
    
    return Path.home() / '.config'


def get_xdg_cache_home() -> Path:
    """Get XDG cache directory for cache files.
    
    Returns XDG_CACHE_HOME if set, otherwise ~/.cache
    
    Returns:
        Path to XDG cache directory
    """
    xdg_cache_home = os.environ.get('XDG_CACHE_HOME')
    if xdg_cache_home:
        return Path(xdg_cache_home)
    
    return Path.home() / '.cache'


def get_eyelet_data_dir(custom_location: Optional[Path] = None) -> Path:
    """Get eyelet data directory for database and logs.
    
    Priority order:
    1. Custom location (if provided)
    2. EYELET_DATA_DIR environment variable
    3. XDG_DATA_HOME/eyelet (if XDG is supported)
    4. ~/.eyelet (fallback)
    
    Args:
        custom_location: Optional custom directory path
        
    Returns:
        Path to eyelet data directory
    """
    # 1. Custom location takes precedence
    if custom_location:
        return custom_location.expanduser().resolve()
    
    # 2. Check environment variable
    eyelet_data_dir = os.environ.get('EYELET_DATA_DIR')
    if eyelet_data_dir:
        return Path(eyelet_data_dir).expanduser().resolve()
    
    # 3. XDG Base Directory if supported (Linux/Unix standard)
    if _supports_xdg():
        return get_xdg_data_home() / 'eyelet'
    
    # 4. Fallback to ~/.eyelet
    return Path.home() / '.eyelet'


def get_eyelet_config_dir(custom_location: Optional[Path] = None) -> Path:
    """Get eyelet configuration directory.
    
    Priority order:
    1. Custom location (if provided)
    2. EYELET_CONFIG_DIR environment variable
    3. XDG_CONFIG_HOME/eyelet (if XDG is supported)
    4. ~/.eyelet (fallback - same as data for simplicity)
    
    Args:
        custom_location: Optional custom directory path
        
    Returns:
        Path to eyelet config directory
    """
    # 1. Custom location takes precedence
    if custom_location:
        return custom_location.expanduser().resolve()
    
    # 2. Check environment variable
    eyelet_config_dir = os.environ.get('EYELET_CONFIG_DIR')
    if eyelet_config_dir:
        return Path(eyelet_config_dir).expanduser().resolve()
    
    # 3. XDG Base Directory if supported
    if _supports_xdg():
        return get_xdg_config_home() / 'eyelet'
    
    # 4. Fallback to ~/.eyelet
    return Path.home() / '.eyelet'


def get_eyelet_db_path(custom_location: Optional[Path] = None, custom_db_name: str = "eyelet.db") -> Path:
    """Get path to eyelet database file.
    
    Args:
        custom_location: Optional custom directory or full file path
        custom_db_name: Custom database filename (default: eyelet.db)
        
    Returns:
        Path to eyelet database file
    """
    # If custom location is a file (ends with .db), use it directly
    if custom_location and custom_location.suffix == '.db':
        return custom_location.expanduser().resolve()
    
    # Otherwise treat as directory and append database filename
    data_dir = get_eyelet_data_dir(custom_location)
    return data_dir / custom_db_name


def _supports_xdg() -> bool:
    """Check if system supports XDG Base Directory specification.
    
    Returns True on Linux/Unix systems, False on macOS/Windows where
    the native conventions are preferred.
    
    Returns:
        True if XDG should be used
    """
    import platform
    
    system = platform.system().lower()
    
    # Use XDG on Linux and other Unix-like systems (but not macOS)
    if system == 'linux':
        return True
    
    # FreeBSD, OpenBSD, etc. also support XDG
    if system in ('freebsd', 'openbsd', 'netbsd'):
        return True
    
    # Don't use XDG on macOS (has its own conventions) or Windows
    return False


def ensure_directory_exists(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to create
        
    Returns:
        The directory path
        
    Raises:
        PermissionError: If directory cannot be created due to permissions
        OSError: If directory cannot be created for other reasons
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except (PermissionError, OSError) as e:
        raise OSError(f"Cannot create directory {path}: {e}") from e


def migrate_legacy_data(legacy_path: Path, new_path: Path) -> bool:
    """Migrate data from legacy location to new XDG-compliant location.
    
    Args:
        legacy_path: Old database file path
        new_path: New database file path
        
    Returns:
        True if migration was performed, False if not needed
    """
    # Only migrate if legacy exists and new doesn't
    if not legacy_path.exists() or new_path.exists():
        return False
    
    try:
        # Ensure new directory exists
        ensure_directory_exists(new_path.parent)
        
        # Copy the database file
        import shutil
        shutil.copy2(legacy_path, new_path)
        
        # Optionally remove old file after successful copy
        # (commented out for safety - user can clean up manually)
        # legacy_path.unlink()
        
        return True
        
    except (PermissionError, OSError):
        # Migration failed - continue with legacy path
        return False