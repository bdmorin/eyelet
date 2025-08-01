"""Logs Viewer Screen"""

from datetime import datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static


class LogsScreen(Screen):
    """Screen for viewing logs"""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "filter", "Filter"),
        Binding("s", "search", "Search"),
        Binding("e", "export", "Export"),
        Binding("q", "app.pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the logs screen"""
        yield Header(show_clock=True)
        yield Container(
            Static("📋 View Logs", classes="screen-header"),
            Vertical(
                Horizontal(
                    Input(placeholder="🔍 Search logs...", id="search-input"),
                    Button("🔍 Search", id="search-button"),
                    Button("🔄 Refresh", id="refresh", variant="primary"),
                    Button("⬇️  Export", id="export"),
                    classes="action-bar",
                ),
                Horizontal(
                    Button("All", id="filter-all", variant="primary"),
                    Button("Errors", id="filter-errors", variant="error"),
                    Button("Warnings", id="filter-warnings", variant="warning"),
                    Button("Success", id="filter-success", variant="success"),
                    Label("│"),
                    Button("Today", id="filter-today"),
                    Button("This Week", id="filter-week"),
                    classes="action-bar",
                ),
                DataTable(id="logs-table", classes="hook-list"),
                Static("", id="log-summary", classes="status-message"),
                id="logs-content",
            ),
            id="logs-container",
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        self.load_logs()
        self.update_summary()
    
    def load_logs(self) -> None:
        """Load logs into the table"""
        table = self.query_one("#logs-table", DataTable)
        
        # Add columns
        table.add_columns("Time", "Type", "Tool", "Status", "Message")
        
        # TODO: Load actual logs from database/files
        # For now, add sample data
        now = datetime.now()
        table.add_row(
            now.strftime("%H:%M:%S"),
            "PreToolUse",
            "Bash",
            "✅",
            "Command: git status"
        )
        table.add_row(
            now.strftime("%H:%M:%S"),
            "PostToolUse",
            "Bash",
            "✅",
            "Success: 0"
        )
        table.add_row(
            now.strftime("%H:%M:%S"),
            "PreToolUse",
            "Edit",
            "🚫",
            "Blocked: rm -rf /"
        )
        table.add_row(
            now.strftime("%H:%M:%S"),
            "UserPromptSubmit",
            "-",
            "✅",
            "Prompt: Help me fix this bug"
        )
    
    def update_summary(self) -> None:
        """Update the summary statistics"""
        summary = self.query_one("#log-summary", Static)
        # TODO: Calculate real statistics
        summary.update("📊 Total: 156 | ✅ Success: 142 | ⚠️  Warnings: 10 | ❌ Errors: 4")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "search-button":
            self.action_search()
        elif button_id == "refresh":
            self.action_refresh()
        elif button_id == "export":
            self.action_export()
        elif button_id.startswith("filter-"):
            filter_type = button_id.replace("filter-", "")
            self.apply_filter(filter_type)
    
    def action_search(self) -> None:
        """Search logs"""
        search_input = self.query_one("#search-input", Input)
        query = search_input.value
        self.app.notify(f"🔍 Searching for: {query}", severity="information")
    
    def action_refresh(self) -> None:
        """Refresh logs"""
        self.app.notify("🔄 Refreshing logs...", severity="information")
        self.load_logs()
        self.update_summary()
    
    def action_filter(self) -> None:
        """Show filter dialog"""
        self.app.notify("🔍 Advanced filter dialog coming soon!", severity="information")
    
    def action_export(self) -> None:
        """Export logs"""
        self.app.notify("⬇️  Export dialog coming soon!", severity="information")
    
    def apply_filter(self, filter_type: str) -> None:
        """Apply a filter to the logs"""
        self.app.notify(f"🔍 Applying filter: {filter_type}", severity="information")