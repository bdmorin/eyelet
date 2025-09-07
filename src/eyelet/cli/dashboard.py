"""Dashboard CLI command for monitoring eyelet databases."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from eyelet.services.metrics_service import MetricsService


@click.group()
def dashboard():
    """Monitor eyelet databases across the system.
    
    Available interfaces:
    - tui: Textual-based terminal interface
    - web: Web-based dashboard (requires additional dependencies)
    - both: Launch both TUI and web interfaces
    - metrics: CLI metrics output (no dependencies)
    - hooks: CLI hooks table (no dependencies)
    - search: CLI search functionality (no dependencies)
    
    For web features with uvx, use:
    uvx --with fastapi --with "uvicorn[standard]" --with jinja2 eyelet dashboard web
    """
    pass


@dashboard.command()
@click.option(
    "--refresh", 
    "-r", 
    default=5, 
    help="Auto-refresh interval in seconds (0 to disable)"
)
@click.option(
    "--database", 
    "-d", 
    type=click.Path(exists=True, path_type=Path),
    help="Focus on a specific database"
)
def tui(refresh: int, database: Optional[Path]):
    """Launch the TUI dashboard (default)."""
    from eyelet.tui.dashboard_app import DashboardApp
    
    app = DashboardApp(
        refresh_interval=refresh if refresh > 0 else None,
        focus_database=database
    )
    app.run()


@dashboard.command()
@click.option(
    "--port", 
    "-p", 
    default=None,
    type=int,
    help="Port to run web server on (default: 443 if available, otherwise random)"
)
@click.option(
    "--host", 
    "-h", 
    default="localhost", 
    help="Host to bind web server to"
)
@click.option(
    "--dev", 
    is_flag=True, 
    help="Enable development mode with auto-reload"
)
@click.option(
    "--open-browser",
    "-o",
    is_flag=True,
    help="Open browser automatically"
)
def web(port: Optional[int], host: str, dev: bool, open_browser: bool):
    """Launch the web dashboard.
    
    The web dashboard requires additional dependencies. Install options:
    
    \b
    1. Local installation:
       uv add eyelet[web] fastapi uvicorn[standard] jinja2
       eyelet dashboard web --open-browser
    
    \b  
    2. Using uvx with dependencies:
       uvx --with fastapi --with "uvicorn[standard]" --with jinja2 eyelet dashboard web -o
    
    \b
    3. CLI-only alternative (no web dependencies):
       uvx eyelet dashboard metrics
       uvx eyelet dashboard hooks
       uvx eyelet dashboard search "query"
    """
    try:
        import uvicorn
        from eyelet.web.dashboard_app import create_dashboard_app
        from eyelet.utils.network import find_available_port, get_sslip_url
    except ImportError:
        click.echo("Web dashboard requires additional dependencies.", err=True)
        click.echo("Install with: uv add fastapi uvicorn[standard] jinja2", err=True)
        sys.exit(1)
    
    # Determine port to use
    if port is None:
        port = find_available_port(host, preferred_port=443)
        click.echo(f"Using port {port}")
    else:
        # User specified port - check if available
        from eyelet.utils.network import is_port_available
        if not is_port_available(host, port):
            click.echo(f"Port {port} is not available. Finding alternative...", err=True)
            port = find_available_port(host, preferred_port=port)
            click.echo(f"Using port {port} instead")
    
    app = create_dashboard_app()
    
    # Generate sslip.io URL
    scheme = "https" if port == 443 else "http"
    sslip_url = get_sslip_url(host, port, scheme)
    
    click.echo(f"🚀 Dashboard available at: {sslip_url}")
    
    if open_browser:
        import webbrowser
        webbrowser.open(sslip_url)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=dev,
        log_level="info" if dev else "warning"
    )


@dashboard.command()
@click.option(
    "--web-port", 
    default=None,
    type=int, 
    help="Port for web interface (default: 443 if available, otherwise random)"
)
@click.option(
    "--host", 
    "-h", 
    default="localhost", 
    help="Host for web interface"
)
@click.option(
    "--refresh", 
    "-r", 
    default=5, 
    help="TUI refresh interval in seconds"
)
def both(web_port: Optional[int], host: str, refresh: int):
    """Launch both TUI and web dashboard.
    
    Requires web dependencies. Install with:
    uvx --with fastapi --with "uvicorn[standard]" --with jinja2 eyelet dashboard both
    """
    import threading
    import time
    import webbrowser
    
    # Import required components
    try:
        import uvicorn
        from eyelet.web.dashboard_app import create_dashboard_app
        from eyelet.tui.dashboard_app import DashboardApp
        from eyelet.utils.network import find_available_port, get_sslip_url
    except ImportError:
        click.echo("Both mode requires web dashboard dependencies.", err=True)
        click.echo("Install with: uv add fastapi uvicorn[standard] jinja2", err=True)
        sys.exit(1)
    
    # Determine web port
    if web_port is None:
        web_port = find_available_port(host, preferred_port=443)
        click.echo(f"Using web port {web_port}")
    else:
        from eyelet.utils.network import is_port_available
        if not is_port_available(host, web_port):
            click.echo(f"Port {web_port} not available. Finding alternative...", err=True)
            web_port = find_available_port(host, preferred_port=web_port)
            click.echo(f"Using web port {web_port} instead")
    
    # Generate sslip.io URL
    scheme = "https" if web_port == 443 else "http"
    sslip_url = get_sslip_url(host, web_port, scheme)
    
    click.echo(f"Starting web dashboard at {sslip_url}")
    
    # Start web server in background thread
    web_app = create_dashboard_app()
    web_thread = threading.Thread(
        target=uvicorn.run,
        kwargs={
            "app": web_app,
            "host": host,
            "port": web_port,
            "log_level": "warning"
        },
        daemon=True
    )
    web_thread.start()
    
    # Give web server time to start
    time.sleep(1)
    
    # Open browser
    webbrowser.open(sslip_url)
    
    click.echo("Starting TUI dashboard...")
    click.echo(f"🚀 Web interface available at {sslip_url}")
    
    # Start TUI in main thread
    tui_app = DashboardApp(
        refresh_interval=refresh if refresh > 0 else None
    )
    tui_app.run()


@dashboard.command()
@click.option(
    "--format", 
    "-f", 
    type=click.Choice(["json", "table", "summary"]),
    default="summary",
    help="Output format"
)
@click.option(
    "--database", 
    "-d", 
    type=click.Path(exists=True, path_type=Path),
    help="Show metrics for specific database only"
)
@click.pass_context
def metrics(ctx, format: str, database: Optional[Path]):
    """Show database metrics without interactive interface."""
    # Use global database setting if no specific database provided
    if not database:
        database = ctx.obj.get("database")
    
    metrics_service = MetricsService(custom_db_path=database)
    
    if database:
        # Show metrics for specific database
        db_metrics = metrics_service.get_database_metrics(database)
        
        if format == "json":
            import json
            # Convert dataclass to dict for JSON serialization
            metrics_dict = {
                "path": str(db_metrics.path),
                "exists": db_metrics.exists,
                "record_count": db_metrics.record_count,
                "last_activity": db_metrics.last_activity.isoformat() if db_metrics.last_activity else None,
                "activity_level": db_metrics.activity_level.value,
                "schema_version": db_metrics.schema_version.value,
                "recent_errors": db_metrics.recent_errors,
                "size_bytes": db_metrics.size_bytes,
                "sessions": db_metrics.sessions,
                "hook_types": db_metrics.hook_types,
                "tools": db_metrics.tools,
                "error_rate": db_metrics.error_rate
            }
            click.echo(json.dumps(metrics_dict, indent=2))
        else:
            _print_database_metrics(db_metrics)
    else:
        # Show system-wide metrics
        system_metrics = metrics_service.get_system_metrics()
        
        if format == "json":
            import json
            # Convert system metrics to dict
            system_dict = {
                "total_databases": system_metrics.total_databases,
                "total_records": system_metrics.total_records,
                "active_databases": system_metrics.active_databases,
                "total_errors": system_metrics.total_errors,
                "unique_sessions": system_metrics.unique_sessions,
                "last_updated": system_metrics.last_updated.isoformat(),
                "databases": []
            }
            
            for db in system_metrics.databases:
                db_dict = {
                    "path": str(db.path),
                    "exists": db.exists,
                    "record_count": db.record_count,
                    "last_activity": db.last_activity.isoformat() if db.last_activity else None,
                    "activity_level": db.activity_level.value,
                    "schema_version": db.schema_version.value,
                    "recent_errors": db.recent_errors,
                    "size_bytes": db.size_bytes,
                    "error_rate": db.error_rate
                }
                system_dict["databases"].append(db_dict)
            
            click.echo(json.dumps(system_dict, indent=2))
        elif format == "table":
            _print_metrics_table(system_metrics)
        else:  # summary
            _print_metrics_summary(system_metrics)


@dashboard.command()
@click.option(
    "--limit", 
    "-l", 
    default=20, 
    help="Number of recent hooks to show"
)
@click.option(
    "--database", 
    "-d", 
    type=click.Path(exists=True, path_type=Path),
    help="Show hooks from specific database only"
)
@click.option(
    "--session", 
    "-s", 
    help="Filter by session ID"
)
@click.option(
    "--hook-type", 
    "-t", 
    help="Filter by hook type"
)
@click.option(
    "--tool", 
    help="Filter by tool name"
)
@click.option(
    "--errors-only", 
    is_flag=True, 
    help="Show only hooks with errors"
)
def hooks(limit: int, database: Optional[Path], session: Optional[str], 
          hook_type: Optional[str], tool: Optional[str], errors_only: bool):
    """Show recent hooks across databases."""
    metrics_service = MetricsService()
    
    if database:
        hooks = metrics_service.get_recent_hooks(database, limit)
    else:
        # Get hooks from all databases
        system_metrics = metrics_service.get_system_metrics()
        all_hooks = []
        
        for db_metrics in system_metrics.databases:
            if db_metrics.exists:
                db_hooks = metrics_service.get_recent_hooks(db_metrics.path, limit)
                all_hooks.extend(db_hooks)
        
        # Sort by timestamp and limit
        all_hooks.sort(key=lambda h: h.timestamp, reverse=True)
        hooks = all_hooks[:limit]
    
    # Apply filters
    if session:
        hooks = [h for h in hooks if session.lower() in h.session_id.lower()]
    
    if hook_type:
        hooks = [h for h in hooks if hook_type.lower() in h.hook_type.lower()]
    
    if tool:
        hooks = [h for h in hooks if h.tool_name and tool.lower() in h.tool_name.lower()]
    
    if errors_only:
        hooks = [h for h in hooks if h.error_message]
    
    _print_hooks_table(hooks)


@dashboard.command()
@click.argument("query")
@click.option(
    "--limit", 
    "-l", 
    default=50, 
    help="Maximum results to show"
)
def search(query: str, limit: int):
    """Search for hooks across all databases."""
    metrics_service = MetricsService()
    hooks = metrics_service.search_hooks(query, limit)
    
    if not hooks:
        click.echo(f"No hooks found matching '{query}'")
        return
    
    click.echo(f"Found {len(hooks)} hooks matching '{query}':")
    _print_hooks_table(hooks)


def _print_database_metrics(metrics):
    """Print detailed metrics for a single database."""
    click.echo(f"Database: {metrics.path}")
    click.echo(f"Exists: {metrics.exists}")
    
    if not metrics.exists:
        return
    
    click.echo(f"Records: {metrics.record_count:,}")
    click.echo(f"Size: {metrics.size_bytes:,} bytes")
    click.echo(f"Last Activity: {metrics.last_activity or 'Never'}")
    click.echo(f"Activity Level: {metrics.activity_level.value}")
    click.echo(f"Schema: {metrics.schema_version.value}")
    click.echo(f"Recent Errors: {metrics.recent_errors}")
    click.echo(f"Error Rate: {metrics.error_rate:.1f}%")
    
    if metrics.hook_types:
        click.echo("\nHook Types:")
        for hook_type, count in sorted(metrics.hook_types.items(), key=lambda x: x[1], reverse=True):
            click.echo(f"  {hook_type}: {count:,}")
    
    if metrics.tools:
        click.echo("\nTools:")
        for tool, count in sorted(metrics.tools.items(), key=lambda x: x[1], reverse=True)[:10]:
            click.echo(f"  {tool}: {count:,}")


def _print_metrics_summary(metrics):
    """Print summary of system metrics."""
    click.echo(f"Eyelet Database Summary")
    click.echo(f"{'='*50}")
    click.echo(f"Total Databases: {metrics.total_databases}")
    click.echo(f"Total Records: {metrics.total_records:,}")
    click.echo(f"Active Databases: {metrics.active_databases}")
    click.echo(f"Total Errors: {metrics.total_errors}")
    click.echo(f"Unique Sessions: {metrics.unique_sessions}")
    click.echo(f"Last Updated: {metrics.last_updated}")
    
    click.echo(f"\nDatabases:")
    for db in metrics.databases:
        status = "🟢" if db.activity_level.value == "active" else "🟡" if db.activity_level.value == "recent" else "🔴"
        click.echo(f"  {status} {db.path} ({db.record_count:,} records)")


def _print_metrics_table(metrics):
    """Print metrics in table format."""
    click.echo(f"{'Path':<50} {'Records':<10} {'Errors':<8} {'Activity':<10} {'Size':<12}")
    click.echo("-" * 90)
    
    for db in metrics.databases:
        path_str = str(db.path)
        if len(path_str) > 45:
            path_str = "..." + path_str[-42:]
        
        size_str = f"{db.size_bytes:,}B"
        activity_str = db.activity_level.value
        
        click.echo(f"{path_str:<50} {db.record_count:<10,} {db.recent_errors:<8} {activity_str:<10} {size_str:<12}")


def _print_hooks_table(hooks):
    """Print hooks in table format."""
    if not hooks:
        click.echo("No hooks found.")
        return
    
    click.echo(f"{'Time':<12} {'Type':<15} {'Tool':<12} {'Status':<10} {'Duration':<10} {'Session':<15}")
    click.echo("-" * 85)
    
    for hook in hooks:
        time_str = hook.timestamp.strftime("%H:%M:%S")
        hook_type = hook.hook_type[:14]
        tool_name = (hook.tool_name or "")[:11]
        status = (hook.status or "")[:9]
        duration = f"{hook.duration_ms}ms" if hook.duration_ms else "-"
        session = hook.session_id[:14]
        
        # Add error indicator
        if hook.error_message:
            status = "❌ " + status
        
        click.echo(f"{time_str:<12} {hook_type:<15} {tool_name:<12} {status:<10} {duration:<10} {session:<15}")