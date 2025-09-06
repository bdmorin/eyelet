#!/usr/bin/env python3
"""Safe TUI test script with proper cleanup"""

import sys
import signal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from eyelet.tui.app import EyeletApp

def cleanup_terminal():
    """Clean up terminal state"""
    import os
    # Reset terminal modes
    os.system('printf "\\033[?1000l\\033[?1003l\\033[?1015l\\033[?1006l"')
    os.system('printf "\\033[?1049l\\033[?25h\\033[0m"')
    os.system('stty sane')

def signal_handler(signum, frame):
    """Handle signals and cleanup"""
    cleanup_terminal()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        app = EyeletApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup_terminal()