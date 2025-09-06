#!/usr/bin/env python3
"""Test Configure Hooks Screen directly"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from textual.app import App
from eyelet.tui.screens.configure_hooks import ConfigureHooksScreen

class TestApp(App):
    """Test app for Configure Hooks screen"""
    CSS_PATH = "src/eyelet/tui/app.tcss"
    
    def on_mount(self):
        """Mount the configure screen"""
        self.push_screen(ConfigureHooksScreen())

if __name__ == "__main__":
    app = TestApp()
    app.run()