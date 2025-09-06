"""Configuration management commands"""

from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from eyelet.application.services import ConfigurationService, HookService
from eyelet.domain.config import LogFormat, LogScope
from eyelet.domain.models import Handler, HandlerType, Hook, HookType, ToolMatcher
from eyelet.infrastructure.repositories import InMemoryHookRepository
from eyelet.services.config_service import ConfigService

console = Console()


@click.group()
def configure():
    """
    Configure hooks for your project - Set the eyelet!

    Manage hook configurations at project or user scope. Hooks intercept
    AI agent actions and allow you to validate, log, or modify behavior.

    Examples:

        # List all configured hooks
        eyelet configure list

        # Add a new hook interactively
        eyelet configure add

        # Remove a hook by ID
        eyelet configure remove PreToolUse_Bash_0

        # Enable/disable hooks
        eyelet configure enable PreToolUse_Bash_0
        eyelet configure disable PreToolUse_Bash_0

        # Clear all hooks (with confirmation)
        eyelet configure clear

    Hook configurations are stored in .claude/settings.json and are
    non-destructive - they complement any existing Claude settings.
    """
    pass


@configure.command()
@click.option(
    "--scope",
    type=click.Choice(["project", "user"]),
    default="project",
    help="Configuration scope",
)
@click.pass_context
def list(ctx, scope):
    """List current hook configuration - Check the manifest"""
    if ctx.obj is None:
        ctx.obj = {"config_dir": Path.cwd()}
    config_dir = (
        ctx.obj.get("config_dir", Path.cwd()) if scope == "project" else Path.home()
    )
    config_service = ConfigurationService(config_dir)

    try:
        config = config_service.load_configuration()

        if not config.hooks:
            console.print("[yellow]No hooks configured[/yellow]")
            return

        table = Table(title=f"Hook Configuration ({scope})")
        table.add_column("Type", style="cyan")
        table.add_column("Matcher", style="green")
        table.add_column("Handler", style="yellow")
        table.add_column("Enabled", style="magenta")

        for hook in config.hooks:
            table.add_row(
                hook.type,
                hook.matcher or "-",
                f"{hook.handler.type}: {hook.handler.command or hook.handler.workflow or '-'}",
                "✓" if hook.enabled else "✗",
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")


@configure.command()
@click.option(
    "--scope",
    type=click.Choice(["project", "user"]),
    default="project",
    help="Configuration scope",
)
@click.pass_context
def add(ctx, scope):
    """Add a new hook - Splice the mainbrace!"""
    if ctx.obj is None:
        ctx.obj = {"config_dir": Path.cwd()}
    config_dir = (
        ctx.obj.get("config_dir", Path.cwd()) if scope == "project" else Path.home()
    )
    config_service = ConfigurationService(config_dir)
    HookService(InMemoryHookRepository())

    # Interactive hook creation
    console.print("[bold]Adding new hook[/bold]")

    # Select hook type
    hook_types = [ht.value for ht in HookType]
    hook_type = Prompt.ask(
        "Select hook type", choices=hook_types, default=HookType.PRE_TOOL_USE.value
    )

    # Select matcher if applicable
    matcher = None
    if hook_type in [HookType.PRE_TOOL_USE.value, HookType.POST_TOOL_USE.value]:
        tool_matchers = [tm.value for tm in ToolMatcher]
        matcher = Prompt.ask(
            "Select tool matcher", choices=tool_matchers, default=ToolMatcher.ALL.value
        )
    elif hook_type == HookType.PRE_COMPACT.value:
        matcher = Prompt.ask(
            "Select compact trigger", choices=["manual", "auto"], default="manual"
        )

    # Configure handler
    handler_type = Prompt.ask(
        "Select handler type", choices=["command", "workflow"], default="command"
    )

    if handler_type == "command":
        command = Prompt.ask("Enter command to execute")
        handler = Handler(type=HandlerType.COMMAND, command=command)
    else:
        workflow = Prompt.ask("Enter workflow name")
        handler = Handler(type=HandlerType.WORKFLOW, workflow=workflow)

    # Create and save hook
    hook = Hook(
        type=HookType(hook_type),
        matcher=matcher,
        handler=handler,
        description=Prompt.ask("Description (optional)", default=""),
    )

    try:
        # Load current config
        config = config_service.load_configuration()

        # Add new hook
        config.add_hook(hook)

        # Save updated config
        config_service.save_configuration(config)

        console.print("[green]✓ Hook added successfully![/green]")
        console.print(f"ID: {hook.id}")
    except Exception as e:
        console.print(f"[red]Error adding hook: {e}[/red]")


@configure.command()
@click.argument("hook_id")
@click.option(
    "--scope",
    type=click.Choice(["project", "user"]),
    default="project",
    help="Configuration scope",
)
@click.pass_context
def remove(ctx, hook_id, scope):
    """Remove a hook - Cut away the old eyelet"""
    if ctx.obj is None:
        ctx.obj = {"config_dir": Path.cwd()}
    config_dir = (
        ctx.obj.get("config_dir", Path.cwd()) if scope == "project" else Path.home()
    )
    config_service = ConfigurationService(config_dir)

    try:
        config = config_service.load_configuration()

        if config.remove_hook(hook_id):
            config_service.save_configuration(config)
            console.print(f"[green]✓ Hook '{hook_id}' removed[/green]")
        else:
            console.print(f"[yellow]Hook '{hook_id}' not found[/yellow]")
    except Exception as e:
        console.print(f"[red]Error removing hook: {e}[/red]")


@configure.command()
@click.argument("hook_id")
@click.option(
    "--scope",
    type=click.Choice(["project", "user"]),
    default="project",
    help="Configuration scope",
)
@click.pass_context
def enable(ctx, hook_id, scope):
    """Enable a hook - Hoist the colors!"""
    _toggle_hook(ctx, hook_id, scope, enabled=True)


@configure.command()
@click.argument("hook_id")
@click.option(
    "--scope",
    type=click.Choice(["project", "user"]),
    default="project",
    help="Configuration scope",
)
@click.pass_context
def disable(ctx, hook_id, scope):
    """Disable a hook - Strike the colors"""
    _toggle_hook(ctx, hook_id, scope, enabled=False)


def _toggle_hook(ctx, hook_id, scope, enabled):
    """Helper to enable/disable hooks"""
    if ctx.obj is None:
        ctx.obj = {"config_dir": Path.cwd()}
    config_dir = (
        ctx.obj.get("config_dir", Path.cwd()) if scope == "project" else Path.home()
    )
    config_service = ConfigurationService(config_dir)

    try:
        config = config_service.load_configuration()

        hook_found = False
        for hook in config.hooks:
            if hook.id == hook_id:
                hook.enabled = enabled
                hook_found = True
                break

        if hook_found:
            config_service.save_configuration(config)
            action = "enabled" if enabled else "disabled"
            console.print(f"[green]✓ Hook '{hook_id}' {action}[/green]")
        else:
            console.print(f"[yellow]Hook '{hook_id}' not found[/yellow]")
    except Exception as e:
        console.print(f"[red]Error updating hook: {e}[/red]")


@configure.command()
@click.option(
    "--scope",
    type=click.Choice(["project", "user"]),
    default="project",
    help="Configuration scope",
)
@click.option("--force", is_flag=True, help="Clear without confirmation")
@click.pass_context
def clear(ctx, scope, force):
    """Clear all hooks - Abandon ship!"""
    if ctx.obj is None:
        ctx.obj = {"config_dir": Path.cwd()}
    config_dir = (
        ctx.obj.get("config_dir", Path.cwd()) if scope == "project" else Path.home()
    )
    config_service = ConfigurationService(config_dir)

    try:
        config = config_service.load_configuration()
        hook_count = len(config.hooks)

        if hook_count == 0:
            console.print("[yellow]No hooks to clear[/yellow]")
            return

        if not force:
            if not Confirm.ask(f"Clear all {hook_count} hooks?"):
                console.print("[yellow]Cancelled[/yellow]")
                return

        config.hooks = []
        config_service.save_configuration(config)
        console.print(f"[green]✓ Cleared {hook_count} hooks[/green]")
    except Exception as e:
        console.print(f"[red]Error clearing hooks: {e}[/red]")


@configure.command(name="install-all")
@click.option(
    "--scope",
    type=click.Choice(["project", "user"]),
    default="project",
    help="Configuration scope",
)
@click.option(
    "--force", is_flag=True, help="Overwrite existing hooks without confirmation"
)
@click.option(
    "--dev", is_flag=True, help="Use local development wheel instead of public uvx"
)
@click.option(
    "--autoupdate", is_flag=True, help="Pin to @latest for automatic updates"
)
@click.pass_context
def install_all(ctx, scope, force, dev, autoupdate):
    """
    Install universal logging for ALL hooks - Full broadside!

    This command installs a comprehensive hook configuration that logs
    every single Claude Code hook to the ./eyelet-hooks directory.

    Hooks installed:
    - PreToolUse: All tools (Bash, Read, Write, etc.)
    - PostToolUse: All tools
    - UserPromptSubmit
    - Notification
    - Stop
    - SubagentStop
    - PreCompact (manual and auto)

    All hooks will log to: ./eyelet-hooks/{hook_type}/{tool}/{date}/
    """
    # Handle case where ctx.obj is not initialized (e.g., when run via uvx)
    if ctx.obj is None:
        ctx.obj = {"config_dir": Path.cwd()}
    config_dir = (
        ctx.obj.get("config_dir", Path.cwd()) if scope == "project" else Path.home()
    )
    config_service = ConfigurationService(config_dir)

    try:
        config = config_service.load_configuration()

        # Check for existing hooks
        if config.hooks and not force:
            if not Confirm.ask(
                f"This will replace {len(config.hooks)} existing hooks. Continue?"
            ):
                console.print("[yellow]Installation cancelled[/yellow]")
                return

        # Create all hook combinations
        all_hooks = []

        # Determine command based on --dev flag
        if dev:
            # For development, use local wheel with uvx
            # When run via uvx, __file__ is in a temp directory, so use cwd
            cwd = Path.cwd()
            wheel_path = cwd / "dist"
            if not wheel_path.exists():
                console.print(
                    "[red]No dist/ directory found. Run 'uv build' first![/red]"
                )
                return
            wheel_files = list(wheel_path.glob("eyelet-*.whl"))
            if not wheel_files:
                console.print(
                    "[red]No wheel file found in dist/. Run 'uv build' first![/red]"
                )
                return
            latest_wheel = max(wheel_files, key=lambda p: p.stat().st_mtime)
            eyelet_cmd = f"uvx --from {str(latest_wheel)} eyelet execute --log-only"
            console.print(
                f"[yellow]Using development wheel: {latest_wheel.name}[/yellow]"
            )
        else:
            # Use public uvx (requires package to be published to PyPI)
            if autoupdate:
                eyelet_cmd = "uvx eyelet@latest execute --log-only"
                console.print(
                    "[cyan]Using public uvx command with @latest (auto-updates enabled)[/cyan]"
                )
            else:
                eyelet_cmd = "uvx eyelet execute --log-only"
                console.print(
                    "[cyan]Using public uvx command (requires PyPI package)[/cyan]"
                )

        # PreToolUse and PostToolUse for all tools

        for hook_type in [HookType.PRE_TOOL_USE, HookType.POST_TOOL_USE]:
            # Add wildcard matcher for all tools
            hook = Hook(
                type=hook_type,
                matcher=".*",  # Matches all tools
                handler=Handler(type=HandlerType.COMMAND, command=eyelet_cmd),
                description=f"Universal Eyelet logging for all {hook_type.value} events",
            )
            all_hooks.append(hook)

        # Hooks without matchers
        for hook_type in [
            HookType.USER_PROMPT_SUBMIT,
            HookType.NOTIFICATION,
            HookType.STOP,
            HookType.SUBAGENT_STOP,
        ]:
            hook = Hook(
                type=hook_type,
                handler=Handler(type=HandlerType.COMMAND, command=eyelet_cmd),
                description=f"Universal Eyelet logging for {hook_type.value}",
            )
            all_hooks.append(hook)

        # PreCompact with specific matchers
        for matcher in ["manual", "auto"]:
            hook = Hook(
                type=HookType.PRE_COMPACT,
                matcher=matcher,
                handler=Handler(type=HandlerType.COMMAND, command=eyelet_cmd),
                description=f"Universal Eyelet logging for PreCompact ({matcher})",
            )
            all_hooks.append(hook)

        # Clear existing and add all new hooks
        config.hooks = []
        for hook in all_hooks:
            config.add_hook(hook)

        # Save configuration
        config_service.save_configuration(config)

        # Success message
        console.print(
            f"[green]✓ Installed {len(all_hooks)} universal logging hooks![/green]"
        )
        console.print("\n[bold]Hooks installed:[/bold]")

        table = Table()
        table.add_column("Hook Type", style="cyan")
        table.add_column("Matcher", style="green")
        table.add_column("Description", style="white")

        for hook in all_hooks:
            table.add_row(hook.type, hook.matcher or "-", hook.description)

        console.print(table)
        console.print("\n[dim]All hooks will log to: ./eyelet-hooks/[/dim]")
        console.print("[dim]Run 'eyelet logs' to view execution history[/dim]")

    except Exception as e:
        import traceback

        console.print(f"[red]Error installing hooks: {e}[/red]")
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


@configure.command()
@click.option(
    "--format",
    help='Logging format(s) - comma-separated list (e.g., "json", "sqlite", "json,sqlite")',
)
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "both"]),
    help="Logging scope (global ~/.claude, project local, or both)",
)
@click.option("--enabled/--disabled", default=None, help="Enable or disable logging")
@click.option(
    "--global",
    "is_global",
    is_flag=True,
    help="Configure global settings instead of project",
)
@click.pass_context
def logging(ctx, format, scope, enabled, is_global):
    """
    Configure logging settings - Chart the course!

    Configure how Eyelet logs hook executions. You can choose:
    - Format: JSON files, SQLite database, or multiple formats
    - Scope: Global (~/.claude), project-local, or both
    - Enable/disable logging entirely

    Examples:
        # Enable SQLite logging for current project
        eyelet configure logging --format sqlite

        # Use both JSON and SQLite globally
        eyelet configure logging --format json,sqlite --scope global --global

        # Disable logging temporarily
        eyelet configure logging --disabled

        # Show current settings
        eyelet configure logging
    """
    config_service = ConfigService()

    # If no options provided, show current settings
    if format is None and scope is None and enabled is None:
        config = config_service.get_config()
        console.print("\n[bold]Current Logging Configuration[/bold]")
        console.print(f"Format: [cyan]{config.logging.format.value}[/cyan]")
        console.print(f"Scope: [cyan]{config.logging.scope.value}[/cyan]")
        console.print(
            f"Enabled: [cyan]{'Yes' if config.logging.enabled else 'No'}[/cyan]"
        )

        if is_global:
            console.print("\n[dim]Showing global configuration[/dim]")
        else:
            # Check if there's a project override
            project_config = config_service.load_project_config()
            if project_config and project_config.logging:
                console.print(
                    "\n[dim]Project configuration overrides global settings[/dim]"
                )
            else:
                console.print(
                    "\n[dim]Using global configuration (no project override)[/dim]"
                )
        return

    # Load appropriate config
    if is_global:
        config = config_service.load_global_config()
    else:
        config = config_service.load_project_config() or config_service.get_config()

    # Update settings
    changed = False

    if format is not None:
        # Parse comma-separated formats
        formats = [f.strip().lower() for f in format.split(",")]

        # Validate formats
        valid_formats = ["json", "sqlite"]
        for fmt in formats:
            if fmt not in valid_formats:
                console.print(f"[red]Invalid format: {fmt}[/red]")
                console.print(f"Valid formats: {', '.join(valid_formats)}")
                return

        # Determine the LogFormat enum value
        if len(formats) == 1:
            config.logging.format = LogFormat(formats[0])
        elif set(formats) == {"json", "sqlite"}:
            config.logging.format = LogFormat.BOTH
        else:
            # For future expansion when we have more formats
            console.print(
                "[yellow]Warning: Multiple format support currently limited to json,sqlite[/yellow]"
            )
            config.logging.format = LogFormat.BOTH

        changed = True

    if scope is not None:
        config.logging.scope = LogScope(scope)
        changed = True

    if enabled is not None:
        config.logging.enabled = enabled
        changed = True

    if changed:
        # Save the configuration
        if is_global:
            config_service.save_global_config(config)
        else:
            config_service.save_project_config(config)

        console.print("\n[green]✓ Logging configuration updated![/green]")
        console.print(f"Format: [cyan]{config.logging.format.value}[/cyan]")
        console.print(f"Scope: [cyan]{config.logging.scope.value}[/cyan]")
        console.print(
            f"Enabled: [cyan]{'Yes' if config.logging.enabled else 'No'}[/cyan]"
        )

        # Show where config was saved
        saved_path = (
            config_service.global_config_path
            if is_global
            else config_service.project_config_path
        )
        console.print(f"\n[dim]Configuration saved to: {saved_path}[/dim]")

        # Special message for SQLite
        if config.logging.format in [LogFormat.SQLITE, LogFormat.BOTH]:
            console.print("\n[bold cyan]SQLite logging enabled![/bold cyan]")
            console.print("Hook executions will be stored in SQLite databases:")
            if config.logging.scope in [LogScope.GLOBAL, LogScope.BOTH]:
                console.print("  • Global: ~/.claude/eyelet-logs/hooks.db")
            if config.logging.scope in [LogScope.PROJECT, LogScope.BOTH]:
                console.print("  • Project: .eyelet-logs/hooks.db")
            console.print(
                "\n[dim]Use 'eyelet query' commands to explore the data[/dim]"
            )
