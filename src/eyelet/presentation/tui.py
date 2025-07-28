"""Textual TUI for Eyelet"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Footer, Header, Static


class EyeletTUI(App):
    """Main TUI application"""

    CSS = """
    Screen {
        background: $background;
    }

    .menu-button {
        margin: 1;
        width: 100%;
        height: 3;
    }

    .title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 1;
    }

    .subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "configure", "Configure"),
        ("t", "templates", "Templates"),
        ("l", "logs", "Logs"),
        ("d", "discover", "Discover"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("🔗 EYELET", classes="title"),
            Static("Hook Orchestration for AI Agents", classes="subtitle"),
            Static("All hands to the eyelet!", classes="subtitle"),
            Vertical(
                Button("Configure Hooks", variant="primary", classes="menu-button", id="configure"),
                Button("Browse Templates", variant="primary", classes="menu-button", id="templates"),
                Button("View Logs", variant="primary", classes="menu-button", id="logs"),
                Button("Discover Hooks", variant="primary", classes="menu-button", id="discover"),
                Button("Settings", classes="menu-button", id="settings"),
                Button("Help", classes="menu-button", id="help"),
            ),
            id="main-menu"
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
            self.action_discover()
        elif button_id == "settings":
            self.push_screen("settings")
        elif button_id == "help":
            self.push_screen("help")

    def action_configure(self) -> None:
        """Open configuration screen"""
        # Placeholder - would navigate to configuration screen
        self.notify("Configure Hooks - Coming soon!")

    def action_templates(self) -> None:
        """Open templates screen"""
        # Placeholder - would navigate to templates screen
        self.notify("Browse Templates - Coming soon!")

    def action_logs(self) -> None:
        """Open logs screen"""
        # Placeholder - would navigate to logs screen
        self.notify("View Logs - Coming soon!")

    def action_discover(self) -> None:
        """Open discovery screen"""
        # Placeholder - would navigate to discovery screen
        self.notify("Discover Hooks - Coming soon!")


def launch_tui():
    """Launch the TUI application"""
    app = EyeletTUI()
    app.run()
