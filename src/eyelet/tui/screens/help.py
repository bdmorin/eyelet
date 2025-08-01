"""Help Screen"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static
from textual.widgets import RichLog


HELP_CONTENT = """# Eyelet Help

## 🚀 Quick Start

Welcome aboard! Eyelet helps you manage Claude Code hooks with ease.

### Key Concepts

- **Hooks**: Intercept and control Claude's tool usage
- **Templates**: Pre-configured hook sets for common scenarios
- **Logs**: Track all hook executions and results

## ⌨️ Keyboard Shortcuts

### Global
- `Ctrl+Q` - Quit application
- `Ctrl+P` - Command palette (coming soon)
- `Ctrl+T` - Toggle theme
- `Escape` - Go back
- `Tab` - Next element
- `Shift+Tab` - Previous element

### Main Menu
- `C` - Configure hooks
- `T` - Browse templates
- `L` - View logs
- `S` - Settings
- `H` - Help
- `Q` - Quit

### Configure Screen
- `A` - Add new hook
- `E` - Edit selected hook
- `D` - Delete selected hook
- `T` - Test selected hook

### Templates Screen
- `I` - Install template
- `P` - Preview template
- `C` - Create new template

### Logs Screen
- `R` - Refresh logs
- `F` - Filter logs
- `S` - Search logs
- `E` - Export logs

## 🛠️ Common Tasks

### Installing Universal Logging
1. Go to Templates (`T`)
2. Select "Universal Logger"
3. Press `I` to install
4. Configure any variables
5. Save

### Creating a Custom Hook
1. Go to Configure (`C`)
2. Press `A` to add hook
3. Select hook type
4. Enter matcher pattern
5. Configure handler
6. Save

### Searching Logs
1. Go to Logs (`L`)
2. Type in search box
3. Press Enter or click Search
4. Use filters for refinement

## 🚫 Troubleshooting

### Hooks Not Firing
- Check hook is enabled
- Verify matcher pattern
- Test with `eyelet execute test`
- Check logs for errors

### Performance Issues
- Enable SQLite logging
- Clean old logs regularly
- Disable verbose hooks
- Check system resources

## 📚 More Information

- Documentation: [GitHub Wiki](https://github.com/bdmorin/eyelet/wiki)
- Issues: [GitHub Issues](https://github.com/bdmorin/eyelet/issues)
- Discord: Coming soon!

---

*Thread through the eyelet!* ⚓
"""


class HelpScreen(Screen):
    """Screen for help documentation"""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the help screen"""
        yield Header(show_clock=True)
        yield Container(
            Static("❓ Help", classes="screen-header"),
            Vertical(
                RichLog(id="help-content", wrap=True),
                id="help-container",
            ),
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Load help content when mounted"""
        help_log = self.query_one("#help-content", RichLog)
        # Convert markdown-style content to rich text
        for line in HELP_CONTENT.split('\n'):
            if line.startswith('#'):
                # Headers
                level = line.count('#')
                text = line.strip('#').strip()
                help_log.write(f"[bold]{'  ' * (level-1)}{text}[/bold]")
            elif line.strip():
                # Regular text
                help_log.write(line)
            else:
                # Empty line
                help_log.write("")