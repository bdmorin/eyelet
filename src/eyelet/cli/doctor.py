"""Doctor command for diagnosing and fixing configuration issues."""

import json
import os
import sqlite3
from pathlib import Path

import click
from rich.console import Console

from eyelet.domain.config import LogFormat, LogScope
from eyelet.services.config_service import ConfigService
from eyelet.services.sqlite_connection import ProcessLocalConnection

console = Console()


@click.command()
@click.option("--fix", is_flag=True, help="Automatically fix issues where possible")
@click.option("--verbose", is_flag=True, help="Show detailed diagnostic information")
@click.pass_context
def doctor(ctx, fix, verbose):
    """
    Diagnose configuration and system health

    Checks for:
    - Claude Code integration status
    - Configuration file validity
    - Database accessibility
    - Directory permissions
    - Hook command consistency
    """
    console.print("\n🩺 [bold]Eyelet Configuration Health Check[/bold]\n")

    issues = []
    warnings = []
    project_dir = ctx.obj.get("config_dir", Path.cwd()) if ctx.obj else Path.cwd()

    # 1. Check Claude Code Integration
    console.print("[bold]1. Claude Code Integration[/bold]")
    claude_issues = check_claude_integration(project_dir, verbose)
    issues.extend(claude_issues[0])
    warnings.extend(claude_issues[1])

    # 2. Check Configuration Files
    console.print("\n[bold]2. Configuration Files[/bold]")
    config_issues = check_configuration(project_dir, verbose)
    issues.extend(config_issues[0])
    warnings.extend(config_issues[1])

    # 3. Check Logging Infrastructure
    console.print("\n[bold]3. Logging Infrastructure[/bold]")
    logging_issues = check_logging_setup(project_dir, verbose)
    issues.extend(logging_issues[0])
    warnings.extend(logging_issues[1])

    # 4. Check Database Health
    console.print("\n[bold]4. Database Health[/bold]")
    db_issues = check_database_health(project_dir, verbose)
    issues.extend(db_issues[0])
    warnings.extend(db_issues[1])

    # 5. Check System Dependencies
    console.print("\n[bold]5. System Dependencies[/bold]")
    dep_issues = check_dependencies(verbose)
    issues.extend(dep_issues[0])
    warnings.extend(dep_issues[1])

    # Check for version pinning warning specifically
    has_unpinned_warning = any("unpinned eyelet command" in w for w in warnings)
    
    # Summary
    console.print("\n" + "=" * 50 + "\n")

    if not issues and not warnings:
        console.print("✅ [bold green]All systems operational![/bold green]")
        console.print("Your Eyelet configuration is healthy. ⚓")
    else:
        if issues:
            console.print(
                f"❌ [bold red]Found {len(issues)} critical issues[/bold red]"
            )
            for issue in issues:
                console.print(f"   • {issue}")

        if warnings:
            console.print(
                f"\n⚠️  [bold yellow]Found {len(warnings)} warnings[/bold yellow]"
            )
            for warning in warnings:
                console.print(f"   • {warning}")

        if fix:
            console.print("\n🔧 [bold]Attempting fixes...[/bold]")
            fixed = attempt_fixes(issues, warnings, project_dir)
            console.print(f"Fixed {fixed} issues.")
        else:
            console.print(
                "\n💡 Run with [bold]--fix[/bold] to automatically fix issues where possible."
            )
    
    # Special notification for unpinned versions
    if has_unpinned_warning:
        console.print("\n" + "=" * 50)
        console.print("\n🔔 [bold yellow]IMPORTANT: Auto-updates not enabled[/bold yellow]")
        console.print("\nYour eyelet hooks won't automatically get updates.")
        console.print("To enable auto-updates, choose one option:\n")
        console.print("  1. [cyan]eyelet configure install-all --autoupdate[/cyan]")
        console.print("     Reinstalls all hooks with @latest pinning\n")
        console.print("  2. [cyan]uvx --reinstall eyelet@latest execute --log-only[/cyan]")
        console.print("     Manually update individual hooks in settings.json\n")
        console.print("  3. [cyan]pipx upgrade eyelet[/cyan] (if using pipx)")
        console.print("     Updates globally installed version")


def check_claude_integration(
    project_dir: Path, verbose: bool
) -> tuple[list[str], list[str]]:
    """Check Claude Code settings and hook configuration."""
    issues = []
    warnings = []

    # Check for Claude settings
    settings_paths = [
        project_dir / ".claude" / "settings.json",
        Path.home() / ".claude" / "settings.json",
    ]

    settings_found = False
    eyelet_hooks = 0
    total_hooks = 0

    for settings_path in settings_paths:
        if settings_path.exists():
            settings_found = True
            console.print(f"   ✅ Found settings: {settings_path}")

            try:
                with open(settings_path) as f:
                    settings = json.load(f)

                # Check hook configuration
                hooks = settings.get("hooks", {})
                unpinned_commands = []
                for _hook_type, hook_list in hooks.items():
                    if isinstance(hook_list, list):
                        for entry in hook_list:
                            if "hooks" in entry:
                                for hook in entry["hooks"]:
                                    total_hooks += 1
                                    command = hook.get("command", "")
                                    if "eyelet" in command:
                                        eyelet_hooks += 1
                                        # Check if version is pinned
                                        if "uvx eyelet" in command and "@" not in command:
                                            unpinned_commands.append(command[:50] + "..." if len(command) > 50 else command)

                if verbose:
                    console.print(f"   📊 Total hooks: {total_hooks}")
                    console.print(f"   📊 Eyelet hooks: {eyelet_hooks}")
                
                # Warn about unpinned versions
                if unpinned_commands:
                    warnings.append(
                        f"Found {len(unpinned_commands)} unpinned eyelet command(s). "
                        "These won't auto-update. Use 'eyelet configure install-all --autoupdate' "
                        "or add '@latest' to commands manually."
                    )
                    if verbose:
                        for cmd in unpinned_commands[:3]:  # Show first 3
                            console.print(f"      • {cmd}")
                        if len(unpinned_commands) > 3:
                            console.print(f"      • ... and {len(unpinned_commands) - 3} more")

            except Exception as e:
                issues.append(f"Failed to parse {settings_path}: {e}")

            break

    if not settings_found:
        issues.append("No Claude settings.json found")
    elif total_hooks == 0:
        warnings.append("No hooks configured in Claude settings")
    elif eyelet_hooks == 0:
        warnings.append("Eyelet not configured in any hooks")
    else:
        console.print(f"   ✅ Eyelet configured in {eyelet_hooks}/{total_hooks} hooks")

    return issues, warnings


def check_configuration(
    project_dir: Path, verbose: bool
) -> tuple[list[str], list[str]]:
    """Check Eyelet configuration files."""
    issues = []
    warnings = []

    try:
        config_service = ConfigService(project_dir)

        # Check global config
        global_config_exists = config_service.GLOBAL_CONFIG_PATH.exists()
        if global_config_exists:
            console.print(f"   ✅ Global config: {config_service.GLOBAL_CONFIG_PATH}")
            try:
                config_service.load_global_config()
            except Exception as e:
                issues.append(f"Invalid global config: {e}")
        else:
            console.print("   ℹ️  No global config (using defaults)")

        # Check project config
        project_config_exists = config_service.project_config_path.exists()
        if project_config_exists:
            console.print(f"   ✅ Project config: {config_service.project_config_path}")
            try:
                config_service.load_project_config()
            except Exception as e:
                issues.append(f"Invalid project config: {e}")
        else:
            console.print("   ℹ️  No project config (using defaults)")

        # Get merged config
        config = config_service.get_config()

        if verbose:
            console.print(f"   📊 Logging format: {config.logging.format}")
            console.print(f"   📊 Logging scope: {config.logging.scope}")
            console.print(f"   📊 Logging enabled: {config.logging.enabled}")

    except Exception as e:
        issues.append(f"Configuration service error: {e}")

    return issues, warnings


def check_logging_setup(
    project_dir: Path, verbose: bool
) -> tuple[list[str], list[str]]:
    """Check logging directories and permissions."""
    issues = []
    warnings = []

    try:
        config_service = ConfigService(project_dir)
        config = config_service.get_config()
        paths = config_service.get_effective_logging_paths()

        # Check project logging
        if config.logging.scope in [LogScope.PROJECT, LogScope.BOTH]:
            project_path = paths["project"]
            if project_path.exists():
                if os.access(project_path, os.W_OK):
                    console.print(f"   ✅ Project logs: {project_path}")
                else:
                    issues.append(f"No write permission: {project_path}")
            else:
                warnings.append(f"Project log directory doesn't exist: {project_path}")

        # Check global logging
        if config.logging.scope in [LogScope.GLOBAL, LogScope.BOTH]:
            global_path = paths["global"]
            if global_path.exists():
                if os.access(global_path, os.W_OK):
                    console.print(f"   ✅ Global logs: {global_path}")
                else:
                    issues.append(f"No write permission: {global_path}")
            else:
                warnings.append(f"Global log directory doesn't exist: {global_path}")

        # Check .gitignore
        if config.logging.add_to_gitignore:
            gitignore_path = project_dir / ".gitignore"
            if gitignore_path.exists():
                with open(gitignore_path) as f:
                    gitignore_content = f.read()

                log_dirs = [".eyelet-logs", ".eyelet-logging", "eyelet-hooks"]
                missing_ignores = [d for d in log_dirs if d not in gitignore_content]

                if missing_ignores:
                    warnings.append(
                        f"Log directories not in .gitignore: {', '.join(missing_ignores)}"
                    )
                else:
                    console.print("   ✅ Log directories in .gitignore")

    except Exception as e:
        issues.append(f"Logging setup error: {e}")

    return issues, warnings


def check_database_health(
    project_dir: Path, verbose: bool
) -> tuple[list[str], list[str]]:
    """Check SQLite database health."""
    issues = []
    warnings = []

    try:
        config_service = ConfigService(project_dir)
        config = config_service.get_config()

        if config.logging.format not in [LogFormat.SQLITE, LogFormat.BOTH]:
            console.print("   ℹ️  SQLite logging not enabled")
            return issues, warnings

        paths = config_service.get_effective_logging_paths()

        # Check each database
        for location, base_path in paths.items():
            if (config.logging.scope == LogScope.PROJECT and location == "global") or (
                config.logging.scope == LogScope.GLOBAL and location == "project"
            ):
                continue

            db_path = base_path / "eyelet.db"
            if db_path.exists():
                try:
                    conn = ProcessLocalConnection(db_path)
                    db = conn.connection

                    # Check integrity
                    result = db.execute("PRAGMA integrity_check").fetchone()
                    if result[0] == "ok":
                        console.print(f"   ✅ {location.title()} DB integrity: OK")
                    else:
                        issues.append(
                            f"{location.title()} DB integrity check failed: {result[0]}"
                        )

                    # Check stats
                    stats = db.execute("SELECT COUNT(*) FROM hooks").fetchone()
                    console.print(f"   📊 {location.title()} DB records: {stats[0]}")

                    # Check WAL mode
                    wal_mode = db.execute("PRAGMA journal_mode").fetchone()[0]
                    if wal_mode != "wal":
                        warnings.append(
                            f"{location.title()} DB not in WAL mode (currently: {wal_mode})"
                        )

                    if verbose:
                        # Check size
                        db_size = db_path.stat().st_size / (1024 * 1024)
                        console.print(
                            f"   📊 {location.title()} DB size: {db_size:.2f} MB"
                        )

                        # Check WAL size
                        wal_path = db_path.with_suffix(".db-wal")
                        if wal_path.exists():
                            wal_size = wal_path.stat().st_size / (1024 * 1024)
                            if wal_size > 10:
                                warnings.append(
                                    f"Large WAL file ({wal_size:.1f} MB) - consider checkpoint"
                                )

                except Exception as e:
                    issues.append(f"Database error ({location}): {e}")
            else:
                if verbose:
                    console.print(f"   ℹ️  No {location} database yet")

    except Exception as e:
        issues.append(f"Database health check error: {e}")

    return issues, warnings


def check_dependencies(verbose: bool) -> tuple[list[str], list[str]]:
    """Check system dependencies."""
    issues = []
    warnings = []

    # Check Python version
    import sys

    py_version = sys.version_info
    if py_version >= (3, 11):
        console.print(
            f"   ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro}"
        )
    else:
        issues.append(
            f"Python 3.11+ required (found {py_version.major}.{py_version.minor})"
        )

    # Check SQLite version
    try:
        conn = sqlite3.connect(":memory:")
        sqlite_version = conn.execute("SELECT sqlite_version()").fetchone()[0]
        console.print(f"   ✅ SQLite {sqlite_version}")

        # Check for JSON1 extension
        try:
            conn.execute("SELECT json('[]')")
            console.print("   ✅ JSON1 extension available")
        except Exception:
            warnings.append("SQLite JSON1 extension not available")

        conn.close()
    except Exception as e:
        issues.append(f"SQLite error: {e}")

    # Check Git
    try:
        import subprocess

        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"   ✅ {result.stdout.strip()}")
        else:
            warnings.append("Git not found (metadata collection limited)")
    except Exception:
        warnings.append("Git not found (metadata collection limited)")

    return issues, warnings


def attempt_fixes(issues: list[str], warnings: list[str], project_dir: Path) -> int:
    """Attempt to fix issues automatically."""
    fixed = 0

    # Fix missing directories
    for item in issues + warnings:
        if "doesn't exist" in item and ("log directory" in item or "logs:" in item):
            # Extract path from message
            try:
                path_str = item.split(": ")[-1]
                path = Path(path_str.strip())
                path.mkdir(parents=True, exist_ok=True)
                console.print(f"   ✅ Created directory: {path}")
                fixed += 1
            except Exception as e:
                console.print(f"   ❌ Failed to create directory: {e}")

    # Fix .gitignore
    for warning in warnings:
        if "not in .gitignore" in warning:
            gitignore_path = project_dir / ".gitignore"
            if gitignore_path.exists():
                with open(gitignore_path, "a") as f:
                    f.write("\n# Eyelet logging directories\n")
                    f.write(".eyelet-logs/\n")
                    f.write(".eyelet-logging/\n")
                    f.write("eyelet-hooks/\n")
                console.print("   ✅ Updated .gitignore")
                fixed += 1

    # Fix missing Eyelet in hooks
    for warning in warnings:
        if "Eyelet not configured in any hooks" in warning:
            console.print(
                "   ℹ️  Run 'eyelet configure install-all' to add Eyelet to all hooks"
            )

    return fixed


if __name__ == "__main__":
    doctor()
