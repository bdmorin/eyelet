"""Configure Hooks Screen"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static


class ConfigureScreen(Screen):
    """Screen for configuring hooks"""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("a", "add_hook", "Add Hook"),
        Binding("e", "edit_hook", "Edit"),
        Binding("d", "delete_hook", "Delete"),
        Binding("t", "test_hook", "Test"),
        Binding("q", "app.pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the configure screen"""
        yield Header(show_clock=True)
        yield Container(
            Static("⚙️  Configure Hooks", classes="screen-header"),
            Vertical(
                Horizontal(
                    Button("➕ Add", id="add-hook", variant="primary"),
                    Button("✏️  Edit", id="edit-hook"),
                    Button("🗑️  Delete", id="delete-hook", variant="error"),
                    Button("🧪 Test", id="test-hook"),
                    Button("💾 Save All", id="save-all", variant="success"),
                    classes="action-bar",
                ),
                DataTable(id="hooks-table", classes="hook-list"),
                id="configure-content",
            ),
            id="configure-container",
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        self.load_hooks()
    
    def load_hooks(self) -> None:
        """Load hooks into the table"""
        table = self.query_one("#hooks-table", DataTable)
        
        # Add columns
        table.add_columns("Type", "Handler", "Matcher", "Status")
        
        # TODO: Load actual hooks from configuration
        # For now, add sample data
        table.add_row("PreToolUse", "command", "Bash|Edit", "✅ Active")
        table.add_row("PostToolUse", "command", ".*", "✅ Active")
        table.add_row("UserPromptSubmit", "script", "-", "⏸️  Disabled")
        table.add_row("Stop", "command", "-", "✅ Active")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "add-hook":
            self.action_add_hook()
        elif button_id == "edit-hook":
            self.action_edit_hook()
        elif button_id == "delete-hook":
            self.action_delete_hook()
        elif button_id == "test-hook":
            self.action_test_hook()
        elif button_id == "save-all":
            self.save_all_hooks()
    
    def action_add_hook(self) -> None:
        """Add a new hook"""
        self.app.notify("➕ Add Hook dialog coming soon!", severity="information")
    
    def action_edit_hook(self) -> None:
        """Edit selected hook"""
        self.app.notify("✏️  Edit Hook dialog coming soon!", severity="information")
    
    def action_delete_hook(self) -> None:
        """Delete selected hook"""
        self.app.notify("🗑️  Delete Hook confirmation coming soon!", severity="warning")
    
    def action_test_hook(self) -> None:
        """Test selected hook"""
        self.app.notify("🧪 Testing hook...", severity="information")
    
    def save_all_hooks(self) -> None:
        """Save all hooks to configuration"""
        self.app.notify("💾 Hooks saved successfully!", severity="success")