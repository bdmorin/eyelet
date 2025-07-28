"""Hook and tool discovery commands"""

import json

import click
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from eyelet.application.discovery import DiscoveryService
from eyelet.domain.exceptions import DiscoveryError
from eyelet.domain.models import HookType, ToolMatcher

console = Console()


@click.group()
def discover():
    """Discover available hooks and tools - Scan the horizon!"""
    pass


@discover.command()
@click.option('--source', type=click.Choice(['static', 'docs', 'runtime', 'all']),
              default='all', help='Discovery source')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def hooks(source, output_json):
    """Discover all available hook types"""
    discovery_service = DiscoveryService()

    try:
        if source == 'all':
            hook_types = discovery_service.discover_all_hooks()
        elif source == 'static':
            hook_types = discovery_service.get_static_hooks()
        elif source == 'docs':
            hook_types = discovery_service.discover_from_docs()
        elif source == 'runtime':
            hook_types = discovery_service.discover_from_runtime()

        if output_json:
            print(json.dumps([h.value for h in hook_types], indent=2))
        else:
            _display_hooks(hook_types)

    except DiscoveryError as e:
        console.print(f"[red]Discovery error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


@discover.command()
@click.option('--source', type=click.Choice(['static', 'docs', 'runtime', 'all']),
              default='all', help='Discovery source')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def tools(source, output_json):
    """Discover all available tools"""
    discovery_service = DiscoveryService()

    try:
        if source == 'all':
            tools = discovery_service.discover_all_tools()
        elif source == 'static':
            tools = discovery_service.get_static_tools()
        elif source == 'docs':
            tools = discovery_service.discover_tools_from_docs()
        elif source == 'runtime':
            tools = discovery_service.discover_tools_from_runtime()

        if output_json:
            print(json.dumps([t.value for t in tools], indent=2))
        else:
            _display_tools(tools)

    except DiscoveryError as e:
        console.print(f"[red]Discovery error: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


@discover.command()
@click.option('--format', type=click.Choice(['table', 'tree', 'json']),
              default='table', help='Output format')
def matrix(format):
    """Generate the complete hook/tool combination matrix"""
    discovery_service = DiscoveryService()

    try:
        matrix = discovery_service.generate_combination_matrix()

        if format == 'json':
            print(json.dumps(matrix, indent=2))
        elif format == 'tree':
            _display_matrix_tree(matrix)
        else:
            _display_matrix_table(matrix)

    except Exception as e:
        console.print(f"[red]Error generating matrix: {e}[/red]")


@discover.command()
def validate():
    """Validate discovered hooks against Claude Code"""
    discovery_service = DiscoveryService()

    console.print("[bold]Validating hook discovery...[/bold]")

    try:
        validation_results = discovery_service.validate_discovery()

        # Display results
        table = Table(title="Validation Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")

        for component, result in validation_results.items():
            status = "[green]✓[/green]" if result['valid'] else "[red]✗[/red]"
            details = result.get('message', '')
            table.add_row(component, status, details)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Validation error: {e}[/red]")


def _display_hooks(hook_types):
    """Display discovered hook types"""
    table = Table(title="Discovered Hook Types")
    table.add_column("Hook Type", style="cyan")
    table.add_column("Requires Matcher", style="green")
    table.add_column("Description", style="white")

    descriptions = {
        HookType.PRE_TOOL_USE: "Runs before tool execution",
        HookType.POST_TOOL_USE: "Runs after tool execution",
        HookType.NOTIFICATION: "Handles UI notifications",
        HookType.USER_PROMPT_SUBMIT: "Processes user prompts",
        HookType.STOP: "Runs when main agent stops",
        HookType.SUBAGENT_STOP: "Runs when subagent stops",
        HookType.PRE_COMPACT: "Runs before context compaction"
    }

    requires_matcher = {
        HookType.PRE_TOOL_USE: "Yes (Tool)",
        HookType.POST_TOOL_USE: "Yes (Tool)",
        HookType.PRE_COMPACT: "Yes (manual/auto)",
        HookType.NOTIFICATION: "No",
        HookType.USER_PROMPT_SUBMIT: "No",
        HookType.STOP: "No",
        HookType.SUBAGENT_STOP: "No"
    }

    for hook_type in hook_types:
        table.add_row(
            hook_type.value,
            requires_matcher.get(hook_type, "Unknown"),
            descriptions.get(hook_type, "")
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(hook_types)} hook types[/dim]")


def _display_tools(tools):
    """Display discovered tools"""
    table = Table(title="Discovered Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Description", style="white")

    categories = {
        "Task": "Execution",
        "Bash": "System",
        "Glob": "File System",
        "Grep": "Search",
        "Read": "File I/O",
        "Edit": "File I/O",
        "MultiEdit": "File I/O",
        "Write": "File I/O",
        "WebFetch": "Network",
        "WebSearch": "Network"
    }

    descriptions = {
        "Task": "Execute subagent tasks",
        "Bash": "Run shell commands",
        "Glob": "File pattern matching",
        "Grep": "Text search in files",
        "Read": "Read file contents",
        "Edit": "Edit file contents",
        "MultiEdit": "Multiple file edits",
        "Write": "Write file contents",
        "WebFetch": "Fetch web content",
        "WebSearch": "Search the web"
    }

    for tool in tools:
        if tool == ToolMatcher.ALL:
            continue  # Skip wildcard

        table.add_row(
            tool.value,
            categories.get(tool.value, "Other"),
            descriptions.get(tool.value, "")
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(tools) - 1} tools (excluding wildcard)[/dim]")


def _display_matrix_table(matrix):
    """Display combination matrix as a table"""
    table = Table(title="Hook/Tool Combination Matrix")
    table.add_column("Hook Type", style="cyan")
    table.add_column("Valid Matchers", style="green")
    table.add_column("Combinations", style="yellow", justify="right")

    total_combinations = 0

    for hook_type, matchers in matrix.items():
        if matchers:
            matcher_list = ", ".join(matchers[:5])
            if len(matchers) > 5:
                matcher_list += f" (+{len(matchers) - 5} more)"
        else:
            matcher_list = "None"

        combinations = len(matchers) if matchers else 1
        total_combinations += combinations

        table.add_row(
            hook_type,
            matcher_list,
            str(combinations)
        )

    console.print(table)
    console.print(f"\n[bold]Total combinations: {total_combinations}[/bold]")


def _display_matrix_tree(matrix):
    """Display combination matrix as a tree"""
    tree = Tree("Hook/Tool Combinations")

    for hook_type, matchers in matrix.items():
        hook_branch = tree.add(f"[cyan]{hook_type}[/cyan]")

        if matchers:
            for matcher in matchers:
                hook_branch.add(f"[green]{matcher}[/green]")
        else:
            hook_branch.add("[dim]No matchers required[/dim]")

    console.print(tree)
