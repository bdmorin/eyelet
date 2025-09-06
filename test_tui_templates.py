#!/usr/bin/env python3
"""Test Templates screen directly"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from textual.app import App

from eyelet.tui.screens.templates import TemplatesScreen


class TestApp(App):
    """Test app for Templates screen"""

    CSS_PATH = "src/eyelet/tui/app.tcss"

    def on_mount(self):
        """Mount the templates screen"""
        self.push_screen(TemplatesScreen())


if __name__ == "__main__":
    app = TestApp()
    app.run()
