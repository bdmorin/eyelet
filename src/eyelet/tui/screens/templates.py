"""Templates Browser Screen"""

from pathlib import Path
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static, DataTable, ListItem, ListView

from eyelet.application.services import TemplateService
from eyelet.domain.models import Template
from eyelet.infrastructure.repositories import FileTemplateRepository


class TemplateCard(Static):
    """A template card widget"""
    
    def __init__(self, template: Template | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = template
        if template:
            self.update(self.render_card())
    
    def render_card(self) -> str:
        """Render the template card"""
        if not self.template:
            return "No template selected"
        
        tags = " ".join([f"#{tag}" for tag in self.template.tags]) if self.template.tags else ""
        return f"""📦 {self.template.name}
{self.template.description}
🏷️  {self.template.category} {tags}
👤 {self.template.author or 'Unknown'} | v{self.template.version}
🪝 {len(self.template.hooks)} hooks"""


class TemplatesScreen(Screen):
    """Screen for browsing templates"""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("i", "install_template", "Install"),
        Binding("p", "preview_template", "Preview"),
        Binding("c", "create_template", "Create"),
        Binding("r", "reload_templates", "Reload"),
        Binding("q", "app.pop_screen", "Back"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize template service
        templates_dir = Path.home() / ".eyelet" / "templates"
        self.template_service = TemplateService(
            FileTemplateRepository(templates_dir)
        )
        self.templates: list[Template] = []
        self.current_filter = "all"
        self.selected_template: Template | None = None
    
    def compose(self) -> ComposeResult:
        """Compose the templates screen"""
        yield Header(show_clock=True)
        yield Container(
            Static("📚 Browse Templates", classes="screen-header"),
            Vertical(
                Horizontal(
                    Button("🔍 All", id="filter-all", variant="primary"),
                    Button("🔒 Security", id="filter-security"),
                    Button("📊 Monitoring", id="filter-monitoring"),
                    Button("🛠️  Development", id="filter-development"),
                    Button("⭐ Custom", id="filter-custom"),
                    Button("🔄 Reload", id="reload"),
                    classes="action-bar",
                ),
                DataTable(
                    id="templates-table",
                    classes="templates-list",
                    cursor_type="row",
                    show_cursor=True,
                ),
                Container(
                    TemplateCard(id="template-preview", classes="card"),
                    id="preview-container",
                ),
                Horizontal(
                    Button("📥 Install", id="install", variant="primary"),
                    Button("👁️  Preview", id="preview"),
                    Button("➕ Create New", id="create"),
                    classes="action-bar",
                ),
                Static("", id="status-message", classes="status-message"),
                id="templates-content",
            ),
            id="templates-container",
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when screen is mounted"""
        table = self.query_one("#templates-table", DataTable)
        # Add columns
        table.add_columns("Name", "Category", "Description", "Hooks", "Version")
        # Load templates
        self.load_templates()
    
    @work(thread=True)
    def load_templates(self) -> None:
        """Load templates from repository"""
        try:
            self.templates = self.template_service.list_templates()
            self.app.call_from_thread(self.update_table)
            self.app.call_from_thread(
                self.update_status, 
                f"Loaded {len(self.templates)} templates", 
                "success"
            )
        except Exception as e:
            self.app.call_from_thread(
                self.update_status,
                f"Failed to load templates: {e}",
                "error"
            )
    
    def update_table(self) -> None:
        """Update the templates table"""
        table = self.query_one("#templates-table", DataTable)
        table.clear()
        
        # Filter templates
        filtered = self.templates
        if self.current_filter != "all":
            filtered = [
                t for t in self.templates 
                if t.category.lower() == self.current_filter.lower()
            ]
        
        # Add rows
        for i, template in enumerate(filtered):
            table.add_row(
                template.name,
                template.category,
                template.description[:50] + "..." if len(template.description) > 50 else template.description,
                str(len(template.hooks)),
                template.version,
                key=str(i)
            )
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection"""
        if event.row_key:
            idx = int(event.row_key.value)
            filtered = self.templates
            if self.current_filter != "all":
                filtered = [
                    t for t in self.templates 
                    if t.category.lower() == self.current_filter.lower()
                ]
            
            if 0 <= idx < len(filtered):
                self.selected_template = filtered[idx]
                # Update preview
                preview = self.query_one("#template-preview", TemplateCard)
                preview.template = self.selected_template
                preview.update(preview.render_card())
    
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update status message"""
        status = self.query_one("#status-message", Static)
        
        # Add appropriate styling based on type
        if status_type == "success":
            status.add_class("status-success")
            status.remove_class("status-error", "status-info")
        elif status_type == "error":
            status.add_class("status-error")
            status.remove_class("status-success", "status-info")
        else:
            status.add_class("status-info")
            status.remove_class("status-success", "status-error")
        
        status.update(message)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "install":
            self.action_install_template()
        elif button_id == "preview":
            self.action_preview_template()
        elif button_id == "create":
            self.action_create_template()
        elif button_id == "reload":
            self.action_reload_templates()
        elif button_id.startswith("filter-"):
            category = button_id.replace("filter-", "")
            self.filter_templates(category)
    
    def action_install_template(self) -> None:
        """Install selected template"""
        if not self.selected_template:
            self.update_status("⚠️  No template selected", "error")
            return
        
        # TODO: Show install dialog with variable configuration
        self.app.notify(
            f"📥 Installing template: {self.selected_template.name}", 
            severity="information"
        )
    
    def action_preview_template(self) -> None:
        """Preview selected template"""
        if not self.selected_template:
            self.update_status("⚠️  No template selected", "error")
            return
        
        # TODO: Show detailed preview dialog
        self.app.notify(
            f"👁️  Previewing template: {self.selected_template.name}", 
            severity="information"
        )
    
    def action_create_template(self) -> None:
        """Create new template"""
        # TODO: Show template creation wizard
        self.app.notify("➕ Template creation wizard coming soon!", severity="information")
    
    def action_reload_templates(self) -> None:
        """Reload templates from disk"""
        self.update_status("🔄 Reloading templates...", "info")
        self.load_templates()
    
    def filter_templates(self, category: str) -> None:
        """Filter templates by category"""
        self.current_filter = category
        self.update_table()
        
        # Update button states
        for button_id in ["filter-all", "filter-security", "filter-monitoring", 
                         "filter-development", "filter-custom"]:
            button = self.query_one(f"#{button_id}", Button)
            if button_id == f"filter-{category}":
                button.variant = "primary"
            else:
                button.variant = "default"
        
        self.update_status(f"🔍 Showing {category} templates", "info")