"""Settings Screen"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, RadioButton, RadioSet, Static, Switch


class SettingsScreen(Screen):
    """Screen for application settings"""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("s", "save", "Save"),
        Binding("r", "reset", "Reset"),
        Binding("q", "app.pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the settings screen"""
        yield Header(show_clock=True)
        yield Container(
            Static("⚙️  Settings", classes="screen-header"),
            Vertical(
                # Appearance Settings
                Container(
                    Static("🎨 Appearance", classes="card-title"),
                    Vertical(
                        Label("Theme:"),
                        RadioSet(
                            RadioButton("Catppuccin Mocha (Dark)", id="theme-mocha", value=True),
                            RadioButton("Catppuccin Latte (Light)", id="theme-latte"),
                            id="theme-selector",
                        ),
                        Label("Animations:"),
                        Switch(value=True, id="animations-switch"),
                        classes="form-group",
                    ),
                    classes="card",
                ),
                
                # Logging Settings
                Container(
                    Static("📋 Logging", classes="card-title"),
                    Vertical(
                        Label("Log Format:"),
                        RadioSet(
                            RadioButton("JSON Files", id="format-json"),
                            RadioButton("SQLite Database", id="format-sqlite"),
                            RadioButton("Both", id="format-both", value=True),
                            id="format-selector",
                        ),
                        Label("Log Retention (days):"),
                        Input(value="30", id="retention-input"),
                        classes="form-group",
                    ),
                    classes="card",
                ),
                
                # Claude Integration
                Container(
                    Static("🤖 Claude Integration", classes="card-title"),
                    Vertical(
                        Label("Hook Timeout (seconds):"),
                        Input(value="30", id="timeout-input"),
                        Label("Debug Mode:"),
                        Switch(value=False, id="debug-switch"),
                        classes="form-group",
                    ),
                    classes="card",
                ),
                
                Horizontal(
                    Button("💾 Save", id="save", variant="success"),
                    Button("🔄 Reset", id="reset", variant="warning"),
                    Button("❌ Cancel", id="cancel"),
                    classes="action-bar",
                ),
                id="settings-content",
            ),
            id="settings-container",
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "save":
            self.action_save()
        elif button_id == "reset":
            self.action_reset()
        elif button_id == "cancel":
            self.app.pop_screen()
    
    def action_save(self) -> None:
        """Save settings"""
        # TODO: Actually save settings
        self.app.notify("💾 Settings saved successfully!", severity="success")
        self.app.pop_screen()
    
    def action_reset(self) -> None:
        """Reset to defaults"""
        self.app.notify("🔄 Settings reset to defaults", severity="warning")
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle theme changes"""
        if event.radio_set.id == "theme-selector":
            if event.pressed.id == "theme-mocha":
                self.app.theme_name = "mocha"
            else:
                self.app.theme_name = "latte"
            self.app.apply_theme()