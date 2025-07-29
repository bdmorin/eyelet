"""Query command for searching and analyzing hook logs."""

import json
from datetime import datetime, timedelta

import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from eyelet.services.config_service import ConfigService
from eyelet.services.query_service import QueryFilter, QueryService

console = Console()


@click.group()
@click.pass_context
def query(ctx):
    """Query and analyze hook logs - Search the archives!"""
    pass


@query.command()
@click.option("--hook-type", help="Filter by hook type (e.g., PreToolUse)")
@click.option("--tool", help="Filter by tool name (e.g., Bash)")
@click.option("--session", help="Filter by session ID")
@click.option("--since", help='Start time (e.g., "1h", "24h", "2024-01-01")')
@click.option("--status", help="Filter by status (success, error)")
@click.option("--branch", help="Filter by git branch")
@click.option("--errors-only", is_flag=True, help="Show only errors")
@click.option("--limit", default=20, help="Maximum results")
@click.option("--format", type=click.Choice(["table", "json", "raw"]), default="table")
@click.pass_context
def search(
    ctx, hook_type, tool, session, since, status, branch, errors_only, limit, format
):
    """Search hook logs with filters."""
    config_service = ConfigService()
    query_service = QueryService(config_service)

    # Parse since parameter
    since_dt = None
    if since:
        if since.endswith("h"):
            hours = int(since[:-1])
            since_dt = datetime.now() - timedelta(hours=hours)
        elif since.endswith("d"):
            days = int(since[:-1])
            since_dt = datetime.now() - timedelta(days=days)
        else:
            try:
                since_dt = datetime.fromisoformat(since)
            except Exception:
                console.print(f"[red]Invalid since format: {since}[/red]")
                return

    # Build filter
    filter = QueryFilter(
        hook_type=hook_type,
        tool_name=tool,
        session_id=session,
        since=since_dt,
        status=status,
        git_branch=branch,
        has_error=errors_only,
        limit=limit,
    )

    # Execute query
    results = query_service.query(filter)

    if not results:
        console.print("[yellow]No matching logs found[/yellow]")
        return

    # Display results
    if format == "json":
        console.print(json.dumps(results, indent=2, default=str))
    elif format == "raw":
        for result in results:
            console.print(result)
    else:  # table
        table = Table(title=f"Hook Logs ({len(results)} results)")
        table.add_column("Time", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Tool", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Duration", style="magenta")
        table.add_column("Session", style="dim")

        for result in results:
            timestamp = datetime.fromisoformat(result["timestamp"])
            time_str = timestamp.strftime("%H:%M:%S")

            execution = result.get("execution") or {}
            status = execution.get("status", "unknown") if execution else "unknown"
            if status == "error":
                status = f"[red]{status}[/red]"
            elif status == "success":
                status = f"[green]{status}[/green]"

            duration = execution.get("duration_ms", "") if execution else ""
            if duration:
                duration = f"{duration}ms"

            table.add_row(
                time_str,
                result.get("hook_type", ""),
                result.get("tool_name", ""),
                status,
                duration,
                result.get("session_id", "")[:8] + "...",
            )

        console.print(table)


@query.command()
@click.option("--since", default="24h", help='Time period (e.g., "1h", "24h")')
@click.pass_context
def summary(ctx, since):
    """Show summary statistics of hook activity."""
    config_service = ConfigService()
    query_service = QueryService(config_service)

    # Parse since parameter
    if since.endswith("h"):
        hours = int(since[:-1])
        since_dt = datetime.now() - timedelta(hours=hours)
    elif since.endswith("d"):
        days = int(since[:-1])
        since_dt = datetime.now() - timedelta(days=days)
    else:
        since_dt = datetime.now() - timedelta(days=1)

    # Get summary
    stats = query_service.get_summary(since_dt)

    # Display summary
    console.print(f"\n[bold]Hook Activity Summary[/bold] (last {since})")
    console.print(f"Period: {stats['period_start']} to {stats['period_end']}")
    console.print(f"Total hooks: [cyan]{stats['total_hooks']}[/cyan]")
    console.print(f"Unique sessions: [cyan]{stats['unique_sessions']}[/cyan]")
    console.print(f"Errors: [red]{stats['errors']}[/red]")
    console.print(f"Avg duration: [magenta]{stats['avg_duration_ms']}ms[/magenta]")

    # Hook type breakdown
    if stats["by_type"]:
        console.print("\n[bold]By Hook Type:[/bold]")
        for hook_type, count in sorted(
            stats["by_type"].items(), key=lambda x: x[1], reverse=True
        ):
            console.print(f"  {hook_type}: {count}")

    # Tool breakdown
    if stats["by_tool"]:
        console.print("\n[bold]By Tool:[/bold]")
        for tool, count in sorted(
            stats["by_tool"].items(), key=lambda x: x[1], reverse=True
        ):
            console.print(f"  {tool}: {count}")

    # Status breakdown
    if stats["by_status"]:
        console.print("\n[bold]By Status:[/bold]")
        for status, count in sorted(
            stats["by_status"].items(), key=lambda x: x[1], reverse=True
        ):
            if status == "error":
                console.print(f"  [red]{status}: {count}[/red]")
            elif status == "success":
                console.print(f"  [green]{status}: {count}[/green]")
            else:
                console.print(f"  {status}: {count}")


@query.command()
@click.option("--limit", default=10, help="Number of errors to show")
@click.pass_context
def errors(ctx, limit):
    """Show recent errors."""
    config_service = ConfigService()
    query_service = QueryService(config_service)

    # Get recent errors
    errors = query_service.get_recent_errors(limit)

    if not errors:
        console.print("[green]No recent errors found![/green]")
        return

    console.print(f"\n[bold red]Recent Errors ({len(errors)})[/bold red]\n")

    for i, error in enumerate(errors):
        timestamp = datetime.fromisoformat(error["timestamp"])
        execution = error.get("execution", {})
        error_msg = execution.get("error_message", "Unknown error")

        console.print(
            f"[bold]{i + 1}. {timestamp.strftime('%Y-%m-%d %H:%M:%S')}[/bold]"
        )
        console.print(f"   Hook: {error['hook_type']}")
        if error.get("tool_name"):
            console.print(f"   Tool: {error['tool_name']}")
        console.print(f"   Error: [red]{error_msg}[/red]")
        console.print(f"   Session: {error['session_id'][:16]}...")
        console.print()


@query.command()
@click.argument("session_id")
@click.pass_context
def session(ctx, session_id):
    """Show timeline for a specific session."""
    config_service = ConfigService()
    query_service = QueryService(config_service)

    # Get session timeline
    timeline = query_service.get_session_timeline(session_id)

    if not timeline:
        console.print(f"[yellow]No logs found for session {session_id}[/yellow]")
        return

    console.print(f"\n[bold]Session Timeline[/bold] ({session_id})")
    console.print(f"Total events: {len(timeline)}\n")

    for event in timeline:
        timestamp = datetime.fromisoformat(event["timestamp"])
        time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]

        hook_type = event["hook_type"]
        tool_name = event.get("tool_name", "")

        if tool_name:
            console.print(f"[cyan]{time_str}[/cyan] {hook_type} - {tool_name}")
        else:
            console.print(f"[cyan]{time_str}[/cyan] {hook_type}")

        # Show additional details for certain events
        if hook_type == "UserPromptSubmit":
            prompt = event.get("input_data", {}).get("prompt", "")
            if prompt:
                console.print(f"  [dim]Prompt: {prompt[:80]}...[/dim]")
        elif hook_type in ["PreToolUse", "PostToolUse"] and tool_name == "Bash":
            command = (
                event.get("input_data", {}).get("tool_input", {}).get("command", "")
            )
            if command:
                console.print(f"  [dim]Command: {command[:80]}...[/dim]")


@query.command()
@click.argument("search_term")
@click.option("--limit", default=20, help="Maximum results")
@click.pass_context
def grep(ctx, search_term, limit):
    """Search for a term in all log data."""
    config_service = ConfigService()
    query_service = QueryService(config_service)

    # Search logs
    results = query_service.search_logs(search_term, limit)

    if not results:
        console.print(f"[yellow]No logs containing '{search_term}' found[/yellow]")
        return

    console.print(
        f"\n[bold]Search Results[/bold] for '{search_term}' ({len(results)} matches)\n"
    )

    for result in results:
        timestamp = datetime.fromisoformat(result["timestamp"])
        console.print(
            f"[cyan]{timestamp.strftime('%Y-%m-%d %H:%M:%S')}[/cyan] - {result['hook_type']}"
        )

        # Show context where term was found
        # This is a simple implementation - could be enhanced
        data_str = json.dumps(result, indent=2)
        lines = data_str.split("\n")
        for i, line in enumerate(lines):
            if search_term.lower() in line.lower():
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = "\n".join(lines[start:end])
                syntax = Syntax(context, "json", theme="monokai", line_numbers=False)
                console.print(syntax)
                break

        console.print()
