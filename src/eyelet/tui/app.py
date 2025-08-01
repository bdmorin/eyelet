"""Main Eyelet TUI Application"""

from pathlib import Path
from typing import Optional

from rich.console import Console
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Static

from eyelet.tui.screens.configure_hooks import ConfigureHooksScreen
from eyelet.tui.screens.help import HelpScreen
from eyelet.tui.screens.logs import LogsScreen
from eyelet.tui.screens.settings import SettingsScreen
from eyelet.tui.screens.templates import TemplatesScreen
from eyelet.tui.themes import LATTE, MOCHA, get_theme_css


class MainMenu(Screen):
    """Main menu screen"""
    
    BINDINGS = [
        Binding("c", "configure", "Configure"),
        Binding("t", "templates", "Templates"),
        Binding("l", "logs", "Logs"),
        Binding("s", "settings", "Settings"),
        Binding("h", "help", "Help"),
        Binding("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the main menu"""
        yield Header(show_clock=True)
        yield Container(
            Vertical(
                Static("⚓ EYELET", id="title"),
                Static("Hook Orchestration for AI Agents", id="subtitle"),
                Static("Thread through the eyelet!", id="tagline"),
                Container(
                    Button(
                        "⚙️  Configure Hooks",
                        id="configure",
                        variant="primary",
                    ),
                    Button(
                        "📚 Browse Templates",
                        id="templates",
                        variant="primary",
                    ),
                    Button(
                        "📋 View Logs",
                        id="logs",
                        variant="primary",
                    ),
                    Button(
                        "🔍 Discover Hooks",
                        id="discover",
                        variant="primary",
                    ),
                    Button(
                        "⚡ Quick Actions",
                        id="quick",
                        variant="primary",
                    ),
                    Horizontal(
                        Button("⚙️  Settings", id="settings"),
                        Button("❓ Help", id="help"),
                        id="bottom-buttons",
                    ),
                    id="menu-buttons",
                ),
                id="main-content",
            ),
            id="main-container",
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "configure":
            self.action_configure()
        elif button_id == "templates":
            self.action_templates()
        elif button_id == "logs":
            self.action_logs()
        elif button_id == "discover":
            self.app.notify("🔍 Discover Hooks - Coming soon!", severity="information")
        elif button_id == "quick":
            self.show_quick_actions()
        elif button_id == "settings":
            self.action_settings()
        elif button_id == "help":
            self.action_help()
    
    def action_configure(self) -> None:
        """Open configure screen"""
        self.app.push_screen("configure")
    
    def action_templates(self) -> None:
        """Open templates screen"""
        self.app.push_screen("templates")
    
    def action_logs(self) -> None:
        """Open logs screen"""
        self.app.push_screen("logs")
    
    def action_settings(self) -> None:
        """Open settings screen"""
        self.app.push_screen("settings")
    
    def action_help(self) -> None:
        """Open help screen"""
        self.app.push_screen("help")
    
    def show_quick_actions(self) -> None:
        """Show quick actions menu"""
        # TODO: Implement quick actions popup
        self.app.notify("⚡ Quick Actions - Coming soon!", severity="information")


class EyeletApp(App):
    """Main Eyelet TUI Application"""
    
    CSS_PATH = "app.tcss"
    TITLE = "Eyelet - Hook Orchestration"
    SUB_TITLE = "Thread through the eyelet!"
    
    SCREENS = {
        "main": MainMenu,
        "configure": ConfigureHooksScreen,
        "templates": TemplatesScreen,
        "logs": LogsScreen,
        "settings": SettingsScreen,
        "help": HelpScreen,
    }
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+p", "command_palette", "Command Palette"),
        Binding("ctrl+t", "toggle_theme", "Toggle Theme"),
    ]
    
    def __init__(self, *args, **kwargs):
        """Initialize the app"""
        super().__init__(*args, **kwargs)
        self.theme_name = "mocha"  # Default to dark theme
        self.console = Console()
    
    def on_mount(self) -> None:
        """Called when app is mounted"""
        self.push_screen("main")
        self.apply_theme()
    
    def action_toggle_theme(self) -> None:
        """Toggle between Mocha and Latte themes"""
        self.theme_name = "latte" if self.theme_name == "mocha" else "mocha"
        self.apply_theme()
        self.notify(f"🎨 Switched to {self.theme_name.title()} theme")
    
    def apply_theme(self) -> None:
        """Apply the current theme"""
        theme = MOCHA if self.theme_name == "mocha" else LATTE
        theme_css = get_theme_css(theme)
        
        # For now, just notify - proper CSS injection needs more work
        # TODO: Implement proper dynamic CSS loading
        pass
    
    def action_command_palette(self) -> None:
        """Show command palette"""
        self.notify("🎯 Command Palette - Coming soon!", severity="information")


def launch_tui():
    """Launch the Eyelet TUI"""
    app = EyeletApp()
    app.run()