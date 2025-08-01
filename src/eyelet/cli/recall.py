"""CLI command for searching Claude Code conversations."""

import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text

from eyelet.recall import ConversationLoader, ConversationSearch, SearchFilter
from eyelet.services.config_service import ConfigService
from eyelet.services.sqlite_migrations import MigrationManager

console = Console()


@click.command()
@click.argument('query', required=False, default='')
@click.option('--role', type=click.Choice(['user', 'assistant', 'system']), help='Filter by message role')
@click.option('--tool', help='Filter by tool name')
@click.option('--session', help='Filter by session ID')
@click.option('--since', help='Messages since (e.g., "1h", "24h", "2025-01-01")')
@click.option('--limit', type=int, default=100, help='Maximum results to return')
@click.option('--no-tui', is_flag=True, help='Output raw results without TUI')
def recall(query: str, role: str, tool: str, session: str, since: str, limit: int, no_tui: bool):
    """Recall Claude Code conversations.
    
    Examples:
        eyelet recall "error handling"
        eyelet recall --tool Bash --since 24h
        eyelet recall --role user "how to"
    """
    try:
        # Get database path
        config_service = ConfigService()
        paths = config_service.get_effective_logging_paths()
        
        # Use global database for conversations
        db_path = paths['global'] / 'eyelet.db'
        
        # Ensure database exists and run migrations
        if not db_path.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Run migrations
        migration_manager = MigrationManager(db_path)
        if migration_manager.needs_migration():
            console.print("[yellow]Running database migrations...[/yellow]")
            applied = migration_manager.migrate()
            for migration in applied:
                console.print(f"  ✓ {migration}")
        
        # Check if conversations are loaded
        loader = ConversationLoader(db_path)
        stats = loader.get_loading_stats()
        
        if stats['total_conversations'] == 0:
            console.print("[yellow]No conversations found in database. Loading from Claude Code logs...[/yellow]")
            
            # Load conversations with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Loading conversations...", total=None)
                
                def update_progress(current, total, message):
                    if total:
                        progress.update(task, total=total, completed=current, description=message)
                
                load_stats = loader.load_all_projects(progress_callback=update_progress)
            
            console.print(f"\n[green]✓ Loaded {load_stats['conversations_loaded']} conversations with {load_stats['messages_loaded']} messages[/green]")
            
            if load_stats['errors']:
                console.print(f"[yellow]⚠ {len(load_stats['errors'])} files had errors[/yellow]")
        
        # Parse filters
        search_filter = SearchFilter(limit=limit)
        
        if role:
            search_filter.role = role
        
        if tool:
            search_filter.tool_name = tool
        
        if session:
            search_filter.session_id = session
        
        if since:
            search_filter.since = _parse_since(since)
        
        # Launch TUI or perform search
        if no_tui or not sys.stdout.isatty():
            # CLI mode - just show results
            search_engine = ConversationSearch(db_path)
            results = search_engine.search(query, search_filter)
            
            if not results:
                console.print("[yellow]No results found[/yellow]")
                return
            
            console.print(f"\n[green]Found {len(results)} results:[/green]\n")
            
            for i, result in enumerate(results, 1):
                msg = result.message
                conv = result.conversation
                
                # Format timestamp
                dt = datetime.fromtimestamp(msg.timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                
                # Get project name
                project_name = Path(conv.project_path).name
                
                # Use Text objects to avoid markup parsing errors
                from rich.text import Text
                
                header = Text()
                header.append(f"{i}. {msg.role.upper()}", style="bold")
                header.append(f" - {time_str} - {project_name}")
                console.print(header)
                
                # Print snippet without markup parsing
                snippet_text = Text(f"   {result.snippet}")
                console.print(snippet_text)
                
                if msg.tool_name:
                    tool_text = Text(f"   Tool: {msg.tool_name}", style="dim")
                    console.print(tool_text)
                
                console.print()
        
        else:
            # Launch TUI with recall screen directly
            from textual.app import App
            from eyelet.tui.screens.recall import RecallScreen
            
            class RecallApp(App):
                """Standalone app for recall feature"""
                CSS_PATH = Path(__file__).parent.parent / "tui" / "app.tcss"
                TITLE = "Eyelet Recall - Search Conversations"
                
                def on_mount(self) -> None:
                    """Mount the recall screen directly"""
                    self.push_screen(RecallScreen(db_path, initial_query=query, initial_filter=search_filter))
            
            app = RecallApp()
            app.run()
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        if '--debug' in sys.argv:
            console.print_exception()
        sys.exit(1)


def _parse_since(since_str: str) -> datetime:
    """Parse since string to datetime.
    
    Args:
        since_str: String like "1h", "24h", "2025-01-01"
        
    Returns:
        datetime object
    """
    from datetime import timedelta
    
    now = datetime.now()
    
    # Try parsing as hours
    if since_str.endswith('h'):
        try:
            hours = int(since_str[:-1])
            return now - timedelta(hours=hours)
        except ValueError:
            pass
    
    # Try parsing as days
    if since_str.endswith('d'):
        try:
            days = int(since_str[:-1])
            return now - timedelta(days=days)
        except ValueError:
            pass
    
    # Try parsing as date
    try:
        return datetime.fromisoformat(since_str)
    except ValueError:
        pass
    
    raise ValueError(f"Invalid since format: {since_str}")


if __name__ == '__main__':
    recall()