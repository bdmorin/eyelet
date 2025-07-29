"""CLI utilities and helpers"""

import sys
from functools import wraps

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from eyelet.domain.exceptions import (
    DiscoveryError,
    HookConfigurationError,
    TemplateError,
    WorkflowError,
)

console = Console()


def handle_errors(func):
    """Decorator to handle common errors with helpful messages"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HookConfigurationError as e:
            console.print(Panel(
                Text.from_markup(
                    f"[red]Hook Configuration Error[/red]\n\n"
                    f"{str(e)}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"• Check your hook type and matcher combination\n"
                    f"• Run 'eyelet discover matrix' to see valid combinations\n"
                    f"• Ensure your .claude/settings.json is valid JSON"
                ),
                title="⚠️  Configuration Issue",
                border_style="red"
            ))
            sys.exit(1)
        except TemplateError as e:
            console.print(Panel(
                Text.from_markup(
                    f"[red]Template Error[/red]\n\n"
                    f"{str(e)}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"• Run 'eyelet template list' to see available templates\n"
                    f"• Check template variables with 'eyelet template show'\n"
                    f"• Verify the template file is valid JSON"
                ),
                title="⚠️  Template Issue",
                border_style="red"
            ))
            sys.exit(1)
        except WorkflowError as e:
            console.print(Panel(
                Text.from_markup(
                    f"[red]Workflow Error[/red]\n\n"
                    f"{str(e)}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"• Check your workflow definition file\n"
                    f"• Ensure all workflow steps are valid\n"
                    f"• Review workflow logs for details"
                ),
                title="⚠️  Workflow Issue",
                border_style="red"
            ))
            sys.exit(1)
        except DiscoveryError as e:
            console.print(Panel(
                Text.from_markup(
                    f"[red]Discovery Error[/red]\n\n"
                    f"{str(e)}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"• Use '--source static' for offline discovery\n"
                    f"• Check your internet connection\n"
                    f"• Update Eyelet to the latest version"
                ),
                title="⚠️  Discovery Issue",
                border_style="red"
            ))
            sys.exit(1)
        except FileNotFoundError as e:
            console.print(Panel(
                Text.from_markup(
                    f"[red]File Not Found[/red]\n\n"
                    f"{str(e)}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"• Check the file path is correct\n"
                    f"• Ensure you have read permissions\n"
                    f"• Use absolute paths when unsure"
                ),
                title="⚠️  File Issue",
                border_style="red"
            ))
            sys.exit(1)
        except PermissionError as e:
            console.print(Panel(
                Text.from_markup(
                    f"[red]Permission Denied[/red]\n\n"
                    f"{str(e)}\n\n"
                    f"[dim]Try:[/dim]\n"
                    f"• Check file/directory permissions\n"
                    f"• Run with appropriate user privileges\n"
                    f"• Ensure the directory is writable"
                ),
                title="⚠️  Permission Issue",
                border_style="red"
            ))
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            sys.exit(130)
        except Exception as e:
            console.print(Panel(
                Text.from_markup(
                    f"[red]Unexpected Error[/red]\n\n"
                    f"{type(e).__name__}: {str(e)}\n\n"
                    f"[dim]This might be a bug. Please report it at:[/dim]\n"
                    f"https://github.com/bdmorin/eyelet/issues\n\n"
                    f"[dim]Include:[/dim]\n"
                    f"• The command you ran\n"
                    f"• This error message\n"
                    f"• Your Eyelet version ({get_version()})"
                ),
                title="⚠️  Unexpected Error",
                border_style="red"
            ))
            if click.get_current_context().obj.get('debug'):
                console.print("\n[dim]Debug trace:[/dim]")
                import traceback
                traceback.print_exc()
            sys.exit(1)
    return wrapper


def get_version():
    """Get the current Eyelet version"""
    try:
        from eyelet import __version__
        return __version__
    except Exception:
        return "unknown"


def confirm_action(message, default=False):
    """Show a confirmation prompt with rich formatting"""
    return click.confirm(
        console.print(f"[yellow]⚠️  {message}[/yellow]", markup=True),
        default=default
    )


def success_message(message):
    """Display a success message"""
    console.print(f"[green]✓[/green] {message}")


def warning_message(message):
    """Display a warning message"""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def error_message(message):
    """Display an error message"""
    console.print(f"[red]✗[/red] {message}")


def info_message(message):
    """Display an info message"""
    console.print(f"[blue]ℹ[/blue] {message}")


class EyeletCommand(click.Command):
    """Enhanced command class with better help formatting"""

    def format_help(self, ctx, formatter):
        """Format help with naval theme and examples"""
        # Command name and description
        console.print(f"\n[bold cyan]{self.name}[/bold cyan] - {self.short_help}")

        if self.help:
            console.print(f"\n{self.help}")

        # Usage
        pieces = self.collect_usage_pieces(ctx)
        if pieces:
            console.print(f"\n[bold]Usage:[/bold] {ctx.command_path} {' '.join(pieces)}")

        # Options
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts.append(rv)

        if opts:
            console.print("\n[bold]Options:[/bold]")
            for opt in opts:
                console.print(f"  {opt[0]:30} {opt[1]}")

        # Epilog
        if self.epilog:
            console.print(f"\n{self.epilog}")


def create_command(name, **attrs):
    """Create a command with enhanced help"""
    attrs.setdefault('cls', EyeletCommand)
    attrs.setdefault('context_settings', {'help_option_names': ['-h', '--help']})
    return click.command(name, **attrs)
