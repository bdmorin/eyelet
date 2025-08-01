"""TUI screen for searching Claude Code conversations."""

from datetime import datetime
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, ListView, ListItem, Static
from rich.text import Text

from eyelet.recall import ConversationSearch, SearchFilter, SearchResult


class RecallScreen(Screen):
    """Screen for searching Claude Code conversations."""
    
    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
        ("q", "quit", "Quit"),
        ("/", "focus_search", "Search"),
        ("enter", "view_message", "View"),
    ]
    
    def __init__(self, db_path: Path, initial_query: str = "", initial_filter: SearchFilter | None = None):
        """Initialize recall screen.
        
        Args:
            db_path: Path to SQLite database
            initial_query: Initial search query
            initial_filter: Initial search filter
        """
        super().__init__()
        self.db_path = db_path
        self.initial_query = initial_query
        self.initial_filter = initial_filter or SearchFilter()
        self.search_engine = ConversationSearch(db_path)
        self.results: list[SearchResult] = []
    
    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        
        with Container(id="recall-container"):
            # Search box
            with Horizontal(id="search-bar"):
                yield Input(
                    placeholder="Search conversations... (e.g., 'error handling', 'tool:Bash')",
                    id="search-input",
                    value=self.initial_query
                )
                yield Button("Search", id="search-button", variant="primary")
            
            # Results area
            yield Label("Results will appear here", id="results-label")
            yield ListView(id="results-list")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Handle mount event."""
        # Focus search input
        self.query_one("#search-input").focus()
        
        # Run initial search if query provided
        if self.initial_query:
            self._perform_search()
    
    @on(Input.Submitted, "#search-input")
    @on(Button.Pressed, "#search-button")
    def search_submitted(self) -> None:
        """Handle search submission."""
        self._perform_search()
    
    def _perform_search(self) -> None:
        """Perform the search and update results."""
        search_input = self.query_one("#search-input", Input)
        query = search_input.value.strip()
        
        if not query:
            self.query_one("#results-label").update("Enter a search query")
            self.query_one("#results-list").clear()
            return
        
        # Perform search
        try:
            self.results = self.search_engine.search(query, self.initial_filter)
            
            # Update UI
            results_list = self.query_one("#results-list", ListView)
            results_list.clear()
            
            if not self.results:
                self.query_one("#results-label").update("No results found")
                return
            
            self.query_one("#results-label").update(f"Found {len(self.results)} results")
            
            # Add results to list
            for i, result in enumerate(self.results):
                msg = result.message
                conv = result.conversation
                
                # Format timestamp
                dt = datetime.fromtimestamp(msg.timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
                
                # Get project name
                project_name = Path(conv.project_path).name
                
                # Create list item
                item_text = Text()
                item_text.append(f"[{msg.role.upper()}] ", style="bold")
                item_text.append(f"{time_str} - {project_name}\n", style="dim")
                item_text.append(result.snippet, style="")
                
                if msg.tool_name:
                    item_text.append(f"\n[Tool: {msg.tool_name}]", style="dim italic")
                
                results_list.append(ListItem(Static(item_text), id=f"result-{i}"))
        
        except Exception as e:
            self.query_one("#results-label").update(f"Error: {str(e)}")
            self.query_one("#results-list").clear()
    
    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input").focus()
    
    def action_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
    
    def action_view_message(self) -> None:
        """View the selected message in detail."""
        # Get selected item
        results_list = self.query_one("#results-list", ListView)
        if results_list.highlighted_child is None:
            return
        
        # Get result index
        item_id = results_list.highlighted_child.id
        if not item_id or not item_id.startswith("result-"):
            return
        
        try:
            index = int(item_id.split("-")[1])
            if 0 <= index < len(self.results):
                result = self.results[index]
                # TODO: Open detailed view
                self.app.push_screen(MessageDetailScreen(result))
        except (ValueError, IndexError):
            pass


class MessageDetailScreen(Screen):
    """Screen for viewing message details."""
    
    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+c", "copy", "Copy"),
    ]
    
    def __init__(self, result: SearchResult):
        """Initialize detail screen.
        
        Args:
            result: Search result to display
        """
        super().__init__()
        self.result = result
    
    def compose(self) -> ComposeResult:
        """Compose the detail view."""
        yield Header()
        
        msg = self.result.message
        conv = self.result.conversation
        
        with ScrollableContainer(id="detail-container"):
            # Message metadata
            yield Label(f"Session: {msg.session_id}", classes="metadata")
            yield Label(f"Role: {msg.role.upper()}", classes="metadata")
            
            dt = datetime.fromtimestamp(msg.timestamp)
            yield Label(f"Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}", classes="metadata")
            
            if msg.tool_name:
                yield Label(f"Tool: {msg.tool_name}", classes="metadata")
            
            if msg.model:
                yield Label(f"Model: {msg.model}", classes="metadata")
            
            yield Label("─" * 40, classes="separator")
            
            # Message content
            yield Label("Content:", classes="section-header")
            
            # Format content based on type
            content_text = self._format_content(msg.content)
            yield Static(content_text, id="message-content")
        
        yield Footer()
    
    def _format_content(self, content: dict) -> str:
        """Format message content for display.
        
        Args:
            content: Message content dictionary
            
        Returns:
            Formatted string
        """
        # Simple formatting for now
        import json
        return json.dumps(content, indent=2, ensure_ascii=False)
    
    def action_back(self) -> None:
        """Go back to search results."""
        self.app.pop_screen()
    
    def action_copy(self) -> None:
        """Copy message content to clipboard."""
        # TODO: Implement clipboard copy
        pass