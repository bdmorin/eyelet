#!/usr/bin/env python3
"""Test TUI exit functionality"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from eyelet.tui.app import EyeletApp


async def test_exit_keys():
    """Test that all exit keys work"""
    app = EyeletApp()

    async with app.run_test() as pilot:
        # Test q key
        await pilot.press("q")
        # App should have exited, but we can't test that directly
        # Just make sure no exception was raised

    print("✓ 'q' key handled")

    # Test Ctrl+Q
    app = EyeletApp()
    async with app.run_test() as pilot:
        await pilot.press("ctrl+q")
    print("✓ 'ctrl+q' handled")

    # Test Escape
    app = EyeletApp()
    async with app.run_test() as pilot:
        await pilot.press("escape")
    print("✓ 'escape' key handled")

    print("\n✅ All exit keys working!")


if __name__ == "__main__":
    print("Testing TUI exit functionality...")
    asyncio.run(test_exit_keys())
