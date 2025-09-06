#!/usr/bin/env python3
"""Quick TUI test runner - demonstrates Textual testing capabilities"""

import asyncio
import sys
from pathlib import Path

# Add src to path for development testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from eyelet.tui.app import EyeletApp


async def test_basic_interactions():
    """Test basic TUI interactions"""
    print("🧪 Testing Eyelet TUI...")

    async with EyeletApp().run_test() as pilot:
        print("✅ App started successfully")

        # Test theme toggle
        print("🎨 Testing theme toggle...")
        initial_theme = pilot.app.theme_name
        await pilot.press("ctrl+t")
        assert pilot.app.theme_name != initial_theme
        print(f"✅ Theme toggled from {initial_theme} to {pilot.app.theme_name}")

        # Test navigation
        print("🧭 Testing navigation...")
        await pilot.press("c")  # Configure
        await pilot.pause()
        assert pilot.app.screen.name == "configure"
        print("✅ Navigated to Configure screen")

        await pilot.press("escape")  # Back
        await pilot.pause()
        assert pilot.app.screen.name == "main"
        print("✅ Returned to main menu")

        # Test all screens
        screens = [
            ("t", "templates", "Templates"),
            ("l", "logs", "Logs"),
            ("s", "settings", "Settings"),
            ("h", "help", "Help"),
        ]

        for key, screen_name, display_name in screens:
            await pilot.press(key)
            await pilot.pause()
            assert pilot.app.screen.name == screen_name
            print(f"✅ Navigated to {display_name} screen")
            await pilot.press("escape")
            await pilot.pause()

        print("\n🎉 All tests passed!")


async def test_snapshot():
    """Generate a snapshot of the TUI"""
    print("\n📸 Generating TUI snapshot...")

    async with EyeletApp().run_test(size=(80, 24)) as pilot:
        # Capture main menu
        snapshot = pilot.app.screen
        print("\nMain Menu Snapshot:")
        print(snapshot)

        # Navigate to logs and capture
        await pilot.press("l")
        await pilot.pause()
        logs_snapshot = pilot.app.screen
        print("\nLogs Screen Snapshot:")
        print(logs_snapshot)


async def test_performance():
    """Test TUI performance with rapid interactions"""
    print("\n⚡ Testing performance...")

    async with EyeletApp().run_test() as pilot:
        import time

        start = time.time()

        # Rapid navigation test
        for _ in range(20):
            await pilot.press("c")
            await pilot.pause(0.05)
            await pilot.press("escape")
            await pilot.pause(0.05)

        elapsed = time.time() - start
        print(f"✅ Completed 20 screen transitions in {elapsed:.2f}s")
        print(f"   Average: {elapsed / 40:.3f}s per transition")


async def main():
    """Run all tests"""
    print("🚀 Eyelet TUI Testing Suite\n")

    try:
        await test_basic_interactions()
        await test_snapshot()
        await test_performance()

        print("\n✨ All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
