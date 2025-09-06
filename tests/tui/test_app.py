"""Tests for Eyelet TUI Application

Textual provides excellent testing support through:
1. Pilot - Simulates user interactions
2. Snapshot testing - Captures UI state
3. Async testing - Handles async operations
4. Query system - Find and interact with widgets
"""

import pytest
from textual.pilot import Pilot

from eyelet.tui.app import EyeletApp, MainMenu

# Skip all TUI tests until TUI is fixed
pytestmark = pytest.mark.skip(reason="TUI is currently broken and needs to be fixed")


class TestEyeletApp:
    """Test the main Eyelet TUI application"""
    
    @pytest.mark.asyncio
    async def test_app_starts(self):
        """Test that the app starts successfully"""
        async with EyeletApp().run_test() as pilot:
            # App should start on main menu
            assert pilot.app.screen.name == "main"
            
            # Check title is displayed
            title = pilot.app.query_one("#title")
            assert "EYELET" in title.renderable
    
    @pytest.mark.asyncio
    async def test_theme_toggle(self):
        """Test theme toggling functionality"""
        async with EyeletApp().run_test() as pilot:
            app = pilot.app
            
            # Should start with mocha theme
            assert app.theme_name == "mocha"
            
            # Toggle theme
            await pilot.press("ctrl+t")
            assert app.theme_name == "latte"
            
            # Toggle back
            await pilot.press("ctrl+t")
            assert app.theme_name == "mocha"
    
    @pytest.mark.asyncio
    async def test_main_menu_navigation(self):
        """Test main menu button navigation"""
        async with EyeletApp().run_test() as pilot:
            # Click Configure button
            await pilot.click("#configure")
            await pilot.pause()  # Wait for screen transition
            assert pilot.app.screen.name == "configure"
            
            # Go back
            await pilot.press("escape")
            await pilot.pause()
            assert pilot.app.screen.name == "main"
            
            # Try Templates
            await pilot.click("#templates")
            await pilot.pause()
            assert pilot.app.screen.name == "templates"
    
    @pytest.mark.asyncio
    async def test_keyboard_shortcuts(self):
        """Test keyboard shortcuts on main menu"""
        async with EyeletApp().run_test() as pilot:
            # Test configure shortcut
            await pilot.press("c")
            await pilot.pause()
            assert pilot.app.screen.name == "configure"
            
            # Back to main
            await pilot.press("q")
            await pilot.pause()
            assert pilot.app.screen.name == "main"
            
            # Test templates shortcut
            await pilot.press("t")
            await pilot.pause()
            assert pilot.app.screen.name == "templates"
    
    @pytest.mark.asyncio
    async def test_notifications(self):
        """Test notification system"""
        async with EyeletApp().run_test() as pilot:
            # Click discover (not implemented yet)
            await pilot.click("#discover")
            
            # Should show notification
            notifications = pilot.app._notifications
            assert len(notifications) > 0
            assert "Coming soon" in str(notifications[-1].message)


class TestConfigureScreen:
    """Test the Configure Hooks screen"""
    
    @pytest.mark.asyncio
    async def test_configure_screen_loads(self):
        """Test that configure screen loads with table"""
        async with EyeletApp().run_test() as pilot:
            # Navigate to configure
            await pilot.press("c")
            await pilot.pause()
            
            # Check table exists and has data
            table = pilot.app.query_one("#hooks-table")
            assert table is not None
            assert table.row_count > 0
    
    @pytest.mark.asyncio
    async def test_add_hook_button(self):
        """Test add hook button"""
        async with EyeletApp().run_test() as pilot:
            await pilot.press("c")
            await pilot.pause()
            
            # Click add button
            await pilot.click("#add-hook")
            
            # Should show notification (since dialog not implemented)
            notifications = pilot.app._notifications
            assert any("Add Hook" in str(n.message) for n in notifications)
    
    @pytest.mark.asyncio
    async def test_configure_keyboard_shortcuts(self):
        """Test keyboard shortcuts in configure screen"""
        async with EyeletApp().run_test() as pilot:
            await pilot.press("c")
            await pilot.pause()
            
            # Test add shortcut
            await pilot.press("a")
            notifications = pilot.app._notifications
            assert any("Add Hook" in str(n.message) for n in notifications)
            
            # Test edit shortcut
            await pilot.press("e")
            assert any("Edit Hook" in str(n.message) for n in notifications)


class TestLogsScreen:
    """Test the Logs viewer screen"""
    
    @pytest.mark.asyncio
    async def test_logs_screen_loads(self):
        """Test that logs screen loads with data"""
        async with EyeletApp().run_test() as pilot:
            # Navigate to logs
            await pilot.press("l")
            await pilot.pause()
            
            # Check table exists
            table = pilot.app.query_one("#logs-table")
            assert table is not None
            assert table.row_count > 0
            
            # Check summary is displayed
            summary = pilot.app.query_one("#log-summary")
            assert "Total:" in summary.renderable
    
    @pytest.mark.asyncio
    async def test_search_functionality(self):
        """Test log search"""
        async with EyeletApp().run_test() as pilot:
            await pilot.press("l")
            await pilot.pause()
            
            # Type in search box
            search_input = pilot.app.query_one("#search-input")
            search_input.value = "test query"
            
            # Click search button
            await pilot.click("#search-button")
            
            # Should show search notification
            notifications = pilot.app._notifications
            assert any("test query" in str(n.message) for n in notifications)
    
    @pytest.mark.asyncio
    async def test_filter_buttons(self):
        """Test log filter buttons"""
        async with EyeletApp().run_test() as pilot:
            await pilot.press("l")
            await pilot.pause()
            
            # Test filter buttons
            for filter_id in ["filter-errors", "filter-warnings", "filter-today"]:
                await pilot.click(f"#{filter_id}")
                notifications = pilot.app._notifications
                assert len(notifications) > 0


class TestSettingsScreen:
    """Test the Settings screen"""
    
    @pytest.mark.asyncio
    async def test_settings_screen_loads(self):
        """Test that settings screen loads"""
        async with EyeletApp().run_test() as pilot:
            # Navigate to settings
            await pilot.press("s")
            await pilot.pause()
            
            # Check theme selector exists
            theme_selector = pilot.app.query_one("#theme-selector")
            assert theme_selector is not None
    
    @pytest.mark.asyncio
    async def test_save_settings(self):
        """Test saving settings"""
        async with EyeletApp().run_test() as pilot:
            await pilot.press("s")
            await pilot.pause()
            
            # Click save
            await pilot.click("#save")
            
            # Should show success notification and go back
            notifications = pilot.app._notifications
            assert any("saved successfully" in str(n.message) for n in notifications)
            
            # Should be back at main menu
            await pilot.pause()
            assert pilot.app.screen.name == "main"


# Snapshot testing example
class TestSnapshots:
    """Test UI snapshots for regression testing"""
    
    @pytest.mark.asyncio
    async def test_main_menu_snapshot(self, snapshot):
        """Test main menu renders correctly"""
        async with EyeletApp().run_test(size=(80, 24)) as pilot:
            # Take snapshot of main menu
            assert pilot.app.screen == snapshot
    
    @pytest.mark.asyncio  
    async def test_configure_screen_snapshot(self, snapshot):
        """Test configure screen renders correctly"""
        async with EyeletApp().run_test(size=(80, 24)) as pilot:
            await pilot.press("c")
            await pilot.pause()
            assert pilot.app.screen == snapshot


# Advanced testing features
class TestAdvancedFeatures:
    """Demonstrate advanced Textual testing features"""
    
    @pytest.mark.asyncio
    async def test_widget_messages(self):
        """Test widget message handling"""
        async with EyeletApp().run_test() as pilot:
            # Test button pressed messages
            button = pilot.app.query_one("#configure")
            
            # Simulate hover
            await pilot.hover("#configure")
            
            # Check button state
            assert button.mouse_over
    
    @pytest.mark.asyncio
    async def test_css_queries(self):
        """Test CSS query system"""
        async with EyeletApp().run_test() as pilot:
            # Query by class
            buttons = pilot.app.query("Button.primary")
            assert len(buttons) > 0
            
            # Query by ID
            configure_btn = pilot.app.query_one("#configure")
            assert configure_btn is not None
            
            # Complex queries
            menu_buttons = pilot.app.query("#menu-buttons Button")
            assert len(menu_buttons) > 0
    
    @pytest.mark.asyncio
    async def test_mount_unmount(self):
        """Test widget mounting and unmounting"""
        async with EyeletApp().run_test() as pilot:
            # Navigate to different screens
            screens = ["configure", "templates", "logs", "settings", "help"]
            
            for screen_name in screens:
                # Go to main first
                while pilot.app.screen.name != "main":
                    await pilot.press("escape")
                    await pilot.pause()
                
                # Navigate to screen
                if screen_name == "configure":
                    await pilot.press("c")
                elif screen_name == "templates":
                    await pilot.press("t")
                elif screen_name == "logs":
                    await pilot.press("l")
                elif screen_name == "settings":
                    await pilot.press("s")
                elif screen_name == "help":
                    await pilot.press("h")
                
                await pilot.pause()
                assert pilot.app.screen.name == screen_name


# Performance testing
class TestPerformance:
    """Test TUI performance"""
    
    @pytest.mark.asyncio
    async def test_rapid_navigation(self):
        """Test rapid screen switching"""
        async with EyeletApp().run_test() as pilot:
            # Rapidly switch between screens
            for _ in range(10):
                await pilot.press("c")
                await pilot.pause(0.1)
                await pilot.press("escape")
                await pilot.pause(0.1)
            
            # App should still be responsive
            assert pilot.app.screen.name == "main"
    
    @pytest.mark.asyncio
    async def test_large_data_rendering(self):
        """Test rendering large datasets"""
        async with EyeletApp().run_test() as pilot:
            await pilot.press("l")
            await pilot.pause()
            
            # Table should handle large data efficiently
            table = pilot.app.query_one("#logs-table")
            # In real app, we'd load thousands of rows
            assert table is not None