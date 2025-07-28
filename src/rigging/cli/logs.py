"""Log viewing and management commands"""

import click
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.text import Text
import json

from rigging.domain.models import HookType
from rigging.application.services import ExecutionService
from rigging.infrastructure.repositories import SQLiteExecutionRepository
from rigging.infrastructure.database import get_db_path

console = Console()


@click.command()
@click.option('--tail', '-n', type=int, default=50, help='Number of recent entries to show')
@click.option('--hook-type', help='Filter by hook type (e.g., PreToolUse, PostToolUse)')
@click.option('--tool', help='Filter by tool name (e.g., Bash, Read, Write)')
@click.option('--status', type=click.Choice(['success', 'error', 'pending', 'running']),
              help='Filter by execution status')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON for processing')
@click.option('--details', '-d', is_flag=True, help='Show detailed execution information')
@click.option('--follow', '-f', is_flag=True, help='Follow log in real-time (like tail -f)')
@click.option('--since', help='Show logs since timestamp (e.g., "1h", "30m", "2023-01-01")')
@click.option('--until', help='Show logs until timestamp')
def logs(tail, hook_type, tool, status, output_json, details, follow, since, until):
    """
    View hook execution logs - Check the ship's log
    
    \b
    View and analyze hook execution history with powerful filtering options.
    Logs show when hooks fired, what data they received, and their results.
    
    \b
    Examples:
        # View last 20 entries
        rigging logs --tail 20
        
        # Filter by hook type and tool
        rigging logs --hook-type PreToolUse --tool Bash
        
        # Show only errors with details
        rigging logs --status error --details
        
        # Follow logs in real-time
        rigging logs --follow
        
        # View logs from last hour
        rigging logs --since 1h
        
        # Export logs as JSON
        rigging logs --json > logs.json
    
    \b
    Status indicators:
        ✓ Success (green)
        ✗ Error (red)
        ⟳ Running (yellow)
        ◯ Pending (dim)
    
    Use --details to see full input/output data for each execution.
    """
    execution_service = ExecutionService(
        SQLiteExecutionRepository(get_db_path())
    )
    
    if follow:
        # Real-time log following
        console.print("[bold]Following hook executions...[/bold] (Ctrl+C to stop)")
        _follow_logs(execution_service, hook_type, tool, status)
        return
    
    # Get executions
    executions = execution_service.list_executions(
        hook_type=HookType(hook_type) if hook_type else None,
        limit=tail
    )
    
    # Apply additional filters
    if tool:
        executions = [e for e in executions if e.tool_name == tool]
    if status:
        executions = [e for e in executions if e.status == status]
    
    if not executions:
        console.print("[yellow]No executions found[/yellow]")
        return
    
    if output_json:
        # JSON output
        data = [e.model_dump() for e in executions]
        print(json.dumps(data, indent=2, default=str))
    elif details:
        # Detailed view
        _show_detailed_logs(executions)
    else:
        # Table view
        _show_table_logs(executions)


def _show_table_logs(executions):
    """Show logs in table format"""
    table = Table(title="Hook Execution Log")
    table.add_column("Time", style="dim")
    table.add_column("Hook", style="cyan")
    table.add_column("Tool", style="green")
    table.add_column("Status", style="magenta")
    table.add_column("Duration", style="yellow", justify="right")
    
    for exc in reversed(executions):  # Show newest first
        # Format time
        time_str = exc.timestamp.strftime("%H:%M:%S")
        
        # Format status with color
        if exc.status == "success":
            status = Text("✓", style="green")
        elif exc.status == "error":
            status = Text("✗", style="red")
        elif exc.status == "running":
            status = Text("⟳", style="yellow")
        else:
            status = Text("◯", style="dim")
        
        # Format duration
        duration = f"{exc.duration_ms}ms" if exc.duration_ms else "-"
        
        table.add_row(
            time_str,
            exc.hook_type,
            exc.tool_name or "-",
            status,
            duration
        )
    
    console.print(table)
    
    # Show summary
    total = len(executions)
    success = len([e for e in executions if e.status == "success"])
    errors = len([e for e in executions if e.status == "error"])
    
    console.print(f"\n[dim]Total: {total} | Success: {success} | Errors: {errors}[/dim]")


def _show_detailed_logs(executions):
    """Show detailed log information"""
    for exc in reversed(executions):  # Show newest first
        # Header
        console.print(f"\n[bold cyan]═══ {exc.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ═══[/bold cyan]")
        
        # Basic info
        console.print(f"[bold]Hook:[/bold] {exc.hook_type}")
        if exc.tool_name:
            console.print(f"[bold]Tool:[/bold] {exc.tool_name}")
        console.print(f"[bold]Status:[/bold] ", end="")
        
        if exc.status == "success":
            console.print("[green]Success[/green]")
        elif exc.status == "error":
            console.print("[red]Error[/red]")
        else:
            console.print(f"[yellow]{exc.status}[/yellow]")
        
        if exc.duration_ms:
            console.print(f"[bold]Duration:[/bold] {exc.duration_ms}ms")
        
        # Input data
        if exc.input_data:
            console.print("\n[bold]Input:[/bold]")
            console.print(json.dumps(exc.input_data, indent=2))
        
        # Output data
        if exc.output_data:
            console.print("\n[bold]Output:[/bold]")
            console.print(json.dumps(exc.output_data, indent=2))
        
        # Error message
        if exc.error_message:
            console.print(f"\n[bold red]Error:[/bold red] {exc.error_message}")


def _follow_logs(execution_service, hook_type, tool, status):
    """Follow logs in real-time"""
    import time
    
    last_id = None
    
    try:
        while True:
            # Get recent executions
            executions = execution_service.list_executions(
                hook_type=HookType(hook_type) if hook_type else None,
                limit=10
            )
            
            # Apply filters
            if tool:
                executions = [e for e in executions if e.tool_name == tool]
            if status:
                executions = [e for e in executions if e.status == status]
            
            # Show new executions
            for exc in executions:
                if last_id is None or (exc.id and exc.id > last_id):
                    _print_log_line(exc)
                    if exc.id:
                        last_id = exc.id
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped following logs[/yellow]")


def _print_log_line(exc):
    """Print a single log line"""
    time_str = exc.timestamp.strftime("%H:%M:%S")
    
    # Status indicator
    if exc.status == "success":
        status = "[green]✓[/green]"
    elif exc.status == "error":
        status = "[red]✗[/red]"
    elif exc.status == "running":
        status = "[yellow]⟳[/yellow]"
    else:
        status = "[dim]◯[/dim]"
    
    # Build log line
    parts = [
        f"[dim]{time_str}[/dim]",
        status,
        f"[cyan]{exc.hook_type}[/cyan]"
    ]
    
    if exc.tool_name:
        parts.append(f"[green]{exc.tool_name}[/green]")
    
    if exc.duration_ms:
        parts.append(f"[yellow]{exc.duration_ms}ms[/yellow]")
    
    if exc.error_message:
        parts.append(f"[red]{exc.error_message}[/red]")
    
    console.print(" ".join(parts))