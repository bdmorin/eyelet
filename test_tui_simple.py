#!/usr/bin/env python3
"""Simple TUI test to check basic functionality"""

import sys
from pathlib import Path

# Add src to path for development testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from eyelet.tui.app import launch_tui

if __name__ == "__main__":
    print("Launching Eyelet TUI...")
    print("Press Ctrl+Q to quit")
    print("\nKey bindings:")
    print("- C: Configure Hooks")
    print("- T: Templates")
    print("- L: Logs")
    print("- S: Settings")
    print("- H: Help")
    print("- Arrow keys: Navigate")
    print("\nStarting...")

    try:
        launch_tui()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
