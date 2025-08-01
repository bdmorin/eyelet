"""Configure Hooks Screen - DRY implementation using existing services"""

from pathlib import Path
from typing import List, Optional

from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.message import Message
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Select,
    Static,
    TextArea,
)

from eyelet.application.services import ConfigurationService
from eyelet.domain.models import Handler, HandlerType, Hook, HookType


class HookEditorModal(ModalScreen):
    """Modal dialog for editing a hook"""
    
    CSS = """
    HookEditorModal {
        align: center middle;
    }
    
    #hook-editor {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1;
        background: $surface;
        border: thick $primary;
    }
    
    .form-group {
        margin: 1 0;
    }
    
    .form-buttons {
        margin-top: 2;
        align: center middle;
    }
    """
    
    def __init__(self, hook: Optional[Hook] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hook = hook
        self.is_new = hook is None
    
    def compose(self) -> ComposeResult:
        """Compose the editor modal"""
        with Container(id="hook-editor"):
            yield Static("⚙️  Edit Hook" if self.hook else "➕ Add Hook", classes="screen-header")
            
            # Hook Type
            yield Label("Hook Type:")
            hook_types = [(t.value, t.value) for t in HookType]
            current_type = self.hook.type.value if self.hook else HookType.PreToolUse.value
            yield Select(
                options=hook_types,
                value=current_type,
                id="hook-type-select"
            )
            
            # Matcher (only for certain hook types)
            yield Label("Matcher Pattern:", id="matcher-label")
            yield Input(
                value=self.hook.matcher if self.hook and self.hook.matcher else "",
                placeholder="e.g., Bash|Edit or .* for all",
                id="matcher-input"
            )
            
            # Handler Type
            yield Label("Handler Type:")
            yield RadioSet(
                RadioButton("Command", id="handler-command", value=True),
                RadioButton("Inline", id="handler-inline"),
                RadioButton("Workflow", id="handler-workflow"),
                id="handler-type"
            )
            
            # Handler Configuration
            yield Label("Handler Configuration:", id="handler-label")
            yield TextArea(
                text=self._get_handler_text(),
                id="handler-config",
                language="bash"
            )
            
            # Buttons
            with Horizontal(classes="form-buttons"):
                yield Button("💾 Save", id="save", variant="success")
                yield Button("❌ Cancel", id="cancel")
    
    def _get_handler_text(self) -> str:
        """Get handler text based on current hook"""
        if not self.hook:
            return ""
        
        if self.hook.handler.type == HandlerType.COMMAND:
            return self.hook.handler.command or ""
        elif self.hook.handler.type == HandlerType.INLINE:
            return self.hook.handler.script or ""
        elif self.hook.handler.type == HandlerType.WORKFLOW:
            return self.hook.handler.workflow or ""
        return ""
    
    @on(Select.Changed, "#hook-type-select")
    def on_hook_type_changed(self, event: Select.Changed) -> None:
        """Handle hook type changes"""
        hook_type = HookType(event.value)
        
        # Show/hide matcher based on hook type
        matcher_label = self.query_one("#matcher-label", Label)
        matcher_input = self.query_one("#matcher-input", Input)
        
        if hook_type in [HookType.PreToolUse, HookType.PostToolUse]:
            matcher_label.display = True
            matcher_input.display = True
            matcher_input.placeholder = "e.g., Bash|Edit or .* for all"
        elif hook_type == HookType.PreCompact:
            matcher_label.display = True
            matcher_input.display = True
            matcher_input.placeholder = "manual or auto"
            matcher_input.value = "manual"
        else:
            matcher_label.display = False
            matcher_input.display = False
            matcher_input.value = ""
    
    @on(Button.Pressed, "#save")
    def on_save(self) -> None:
        """Save the hook"""
        # Gather form data
        hook_type = HookType(self.query_one("#hook-type-select", Select).value)
        matcher = self.query_one("#matcher-input", Input).value
        handler_config = self.query_one("#handler-config", TextArea).text
        
        # Determine handler type from radio selection
        handler_type = HandlerType.COMMAND  # default
        radio_set = self.query_one("#handler-type", RadioSet)
        if radio_set.pressed_button:
            if radio_set.pressed_button.id == "handler-inline":
                handler_type = HandlerType.INLINE
            elif radio_set.pressed_button.id == "handler-workflow":
                handler_type = HandlerType.WORKFLOW
        
        # Create handler
        handler = Handler(type=handler_type)
        if handler_type == HandlerType.COMMAND:
            handler.command = handler_config
        elif handler_type == HandlerType.INLINE:
            handler.script = handler_config
        elif handler_type == HandlerType.WORKFLOW:
            handler.workflow = handler_config
        
        # Create hook
        hook = Hook(
            type=hook_type,
            handler=handler,
            matcher=matcher if matcher else None
        )
        
        # Return the hook to the parent screen
        self.dismiss(hook)
    
    @on(Button.Pressed, "#cancel")
    def on_cancel(self) -> None:
        """Cancel editing"""
        self.dismiss(None)


class ConfigureHooksScreen(Screen):
    """Configure Hooks screen using existing ConfigurationService"""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("a", "add_hook", "Add Hook"),
        Binding("e", "edit_hook", "Edit"),
        Binding("d", "delete_hook", "Delete"),
        Binding("t", "test_hook", "Test"),
        Binding("r", "reload", "Reload"),
        Binding("s", "save", "Save"),
        Binding("arrow_up", "move_up", "Up", show=False),
        Binding("arrow_down", "move_down", "Down", show=False),
        Binding("arrow_left", "focus_previous", "Previous", show=False),
        Binding("arrow_right", "focus_next", "Next", show=False),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_service = ConfigurationService(Path.cwd())
        self.hooks: List[Hook] = []
        self.modified = False
    
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
                    Button("🔄 Reload", id="reload"),
                    Button("💾 Save", id="save", variant="success"),
                    classes="action-bar",
                ),
                DataTable(id="hooks-table", classes="hook-list", cursor_type="row", show_cursor=True),
                Static("", id="status-message", classes="status-message"),
                id="configure-content",
            ),
            id="configure-container",
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        self.load_hooks()
    
    @work(thread=True)
    def load_hooks(self) -> None:
        """Load hooks from configuration service"""
        try:
            config = self.config_service.load_configuration()
            self.hooks = config.hooks if config.hooks else []
            self.app.call_from_thread(self.update_table)
            self.app.call_from_thread(self.update_status, f"Loaded {len(self.hooks)} hooks", "success")
        except Exception as e:
            self.app.call_from_thread(self.update_status, f"Failed to load hooks: {e}", "error")
    
    def update_table(self) -> None:
        """Update the hooks table"""
        table = self.query_one("#hooks-table", DataTable)
        
        # Clear and setup columns
        table.clear(columns=True)
        table.add_columns("Type", "Handler", "Matcher", "Status", "Actions")
        
        # Add rows for each hook
        for i, hook in enumerate(self.hooks):
            status = "✅ Active" if getattr(hook, 'enabled', True) else "⏸️  Disabled"
            
            # Format matcher
            matcher = hook.matcher if hook.matcher else "-"
            # Handle both enum and string comparisons
            hook_type_str = hook.type.value if hasattr(hook.type, 'value') else hook.type
            if hook_type_str == "PreCompact":
                matcher = hook.matcher or "manual"
            
            # Handle both enum and string types
            hook_type = hook.type.value if hasattr(hook.type, 'value') else hook.type
            handler_type = hook.handler.type.value if hasattr(hook.handler.type, 'value') else hook.handler.type
            
            table.add_row(
                hook_type,
                handler_type,
                matcher,
                status,
                f"[{i}]",  # Index for actions
                key=str(i)
            )
    
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update status message"""
        status = self.query_one("#status-message", Static)
        
        if status_type == "success":
            status.update(f"[green]✅ {message}[/green]")
        elif status_type == "error":
            status.update(f"[red]❌ {message}[/red]")
        elif status_type == "warning":
            status.update(f"[yellow]⚠️  {message}[/yellow]")
        else:
            status.update(f"[blue]ℹ️  {message}[/blue]")
    
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
        elif button_id == "reload":
            self.action_reload()
        elif button_id == "save":
            self.action_save()
    
    def action_add_hook(self) -> None:
        """Add a new hook"""
        def on_dismiss(hook: Optional[Hook]) -> None:
            if hook:
                self.hooks.append(hook)
                self.modified = True
                self.update_table()
                self.update_status("Hook added", "success")
        
        modal = HookEditorModal()
        self.app.push_screen(modal, on_dismiss)
    
    def action_edit_hook(self) -> None:
        """Edit selected hook"""
        table = self.query_one("#hooks-table", DataTable)
        if table.cursor_row is not None and 0 <= table.cursor_row < len(self.hooks):
            hook = self.hooks[table.cursor_row]
            
            def on_dismiss(edited_hook: Optional[Hook]) -> None:
                if edited_hook:
                    self.hooks[table.cursor_row] = edited_hook
                    self.modified = True
                    self.update_table()
                    self.update_status("Hook updated", "success")
            
            modal = HookEditorModal(hook)
            self.app.push_screen(modal, on_dismiss)
        else:
            self.update_status("No hook selected", "warning")
    
    def action_delete_hook(self) -> None:
        """Delete selected hook"""
        table = self.query_one("#hooks-table", DataTable)
        if table.cursor_row is not None and 0 <= table.cursor_row < len(self.hooks):
            # TODO: Add confirmation dialog
            del self.hooks[table.cursor_row]
            self.modified = True
            self.update_table()
            self.update_status("Hook deleted", "success")
        else:
            self.update_status("No hook selected", "warning")
    
    def action_test_hook(self) -> None:
        """Test selected hook"""
        table = self.query_one("#hooks-table", DataTable)
        if table.cursor_row is not None and 0 <= table.cursor_row < len(self.hooks):
            hook = self.hooks[table.cursor_row]
            self.update_status(f"Testing {hook.type.value} hook...", "info")
            # TODO: Implement actual hook testing
            self.set_timer(2.0, lambda: self.update_status("Hook test completed", "success"))
        else:
            self.update_status("No hook selected", "warning")
    
    def action_reload(self) -> None:
        """Reload hooks from disk"""
        if self.modified:
            self.update_status("Unsaved changes will be lost!", "warning")
            # TODO: Add confirmation dialog
        self.load_hooks()
    
    @work(thread=True)
    def action_save(self) -> None:
        """Save hooks to configuration"""
        try:
            # Get current config
            config = self.config_service.load_configuration()
            
            # Update hooks
            config.hooks = self.hooks
            
            # Save configuration
            self.config_service.save_configuration(config)
            
            self.modified = False
            self.app.call_from_thread(self.update_status, "Configuration saved", "success")
        except Exception as e:
            self.app.call_from_thread(self.update_status, f"Failed to save: {e}", "error")
    
    def action_move_up(self) -> None:
        """Move focus up in the table"""
        table = self.query_one("#hooks-table", DataTable)
        table.action_cursor_up()
    
    def action_move_down(self) -> None:
        """Move focus down in the table"""
        table = self.query_one("#hooks-table", DataTable)
        table.action_cursor_down()