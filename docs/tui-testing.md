# TUI Testing with Textual

Textual provides excellent testing capabilities for TUI applications. This guide covers the testing features available and best practices.

## Testing Features

### 1. Pilot - User Interaction Simulator

The `Pilot` class simulates user interactions programmatically:

```python
async with MyApp().run_test() as pilot:
    # Simulate key presses
    await pilot.press("ctrl+q")
    
    # Click on widgets
    await pilot.click("#button-id")
    
    # Type text
    await pilot.type("Hello, world!")
    
    # Hover over elements
    await pilot.hover("#widget-id")
    
    # Wait for animations
    await pilot.pause()
```

### 2. Widget Queries

Find and interact with widgets using CSS-like selectors:

```python
# Find by ID
button = pilot.app.query_one("#my-button")

# Find by class
buttons = pilot.app.query(".primary")

# Complex queries
menu_items = pilot.app.query("#menu Button.active")
```

### 3. Snapshot Testing

Capture and compare UI states:

```python
@pytest.mark.asyncio
async def test_ui_snapshot(snapshot):
    async with MyApp().run_test(size=(80, 24)) as pilot:
        assert pilot.app.screen == snapshot
```

### 4. Async Testing

All Textual tests are async, allowing proper handling of animations and transitions:

```python
@pytest.mark.asyncio
async def test_async_operation():
    async with MyApp().run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()  # Wait for async operations
        assert pilot.app.screen.name == "expected"
```

## Testing Best Practices

### 1. Use Fixtures for Common Setup

```python
@pytest.fixture
async def app():
    """Fixture for app instance"""
    app = EyeletApp()
    async with app.run_test() as pilot:
        yield pilot

async def test_something(app):
    await app.press("c")
    assert app.app.screen.name == "configure"
```

### 2. Test User Journeys

```python
async def test_complete_workflow():
    """Test a complete user workflow"""
    async with EyeletApp().run_test() as pilot:
        # User opens templates
        await pilot.press("t")
        await pilot.pause()
        
        # Selects a template
        await pilot.click("#template-1")
        
        # Installs it
        await pilot.click("#install")
        await pilot.pause()
        
        # Verifies success
        notifications = pilot.app._notifications
        assert any("success" in str(n.message).lower() for n in notifications)
```

### 3. Test Error Conditions

```python
async def test_error_handling():
    """Test error scenarios"""
    async with EyeletApp().run_test() as pilot:
        # Simulate invalid input
        await pilot.press("c")
        await pilot.pause()
        
        # Try to save without required fields
        await pilot.click("#save")
        
        # Should show error
        assert pilot.app.query(".error")
```

### 4. Performance Testing

```python
async def test_large_dataset_performance():
    """Test with large amounts of data"""
    async with EyeletApp().run_test() as pilot:
        # Load logs screen
        await pilot.press("l")
        await pilot.pause()
        
        # Measure rendering time
        import time
        start = time.time()
        
        # Add many rows
        table = pilot.app.query_one("#logs-table")
        for i in range(1000):
            table.add_row(f"Row {i}", "Data", "More data")
        
        elapsed = time.time() - start
        assert elapsed < 1.0  # Should render in under 1 second
```

## Running Tests

### With pytest

```bash
# Run all TUI tests
pytest tests/tui/

# Run with coverage
pytest tests/tui/ --cov=eyelet.tui

# Run specific test
pytest tests/tui/test_app.py::TestEyeletApp::test_theme_toggle

# Run with verbose output
pytest tests/tui/ -v
```

### Standalone Test Script

```bash
# Run the test script
python test_tui.py
```

## Mock External Dependencies

```python
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_with_mocked_config():
    """Test with mocked configuration service"""
    with patch('eyelet.tui.app.ConfigService') as mock_config:
        mock_config.return_value.get_hooks.return_value = []
        
        async with EyeletApp().run_test() as pilot:
            await pilot.press("c")
            await pilot.pause()
            
            # Verify empty state is shown
            assert pilot.app.query(".empty-state")
```

## Testing Themes

```python
async def test_theme_application():
    """Test theme changes are applied correctly"""
    async with EyeletApp().run_test() as pilot:
        # Get initial colors
        initial_bg = pilot.app.styles.background
        
        # Toggle theme
        await pilot.press("ctrl+t")
        
        # Verify colors changed
        assert pilot.app.styles.background != initial_bg
```

## Debugging Tests

### Enable Debug Output

```python
import os
os.environ["TEXTUAL_DEBUG"] = "1"

async def test_with_debug():
    async with EyeletApp().run_test() as pilot:
        # Debug info will be printed
        await pilot.press("c")
```

### Take Screenshots

```python
async def test_with_screenshot():
    async with EyeletApp().run_test() as pilot:
        # Take screenshot for debugging
        pilot.app.save_screenshot("debug.svg")
```

## CI/CD Integration

### GitHub Actions

```yaml
name: TUI Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest tests/tui/ -v
```

## Common Testing Patterns

### Wait for Specific Conditions

```python
async def test_wait_for_condition():
    async with EyeletApp().run_test() as pilot:
        # Wait for specific widget to appear
        await pilot.wait_for_selector("#dynamic-widget")
        
        # Wait for animation to complete
        await pilot.pause(0.5)
```

### Test Keyboard Navigation

```python
async def test_tab_navigation():
    async with EyeletApp().run_test() as pilot:
        # Tab through elements
        await pilot.press("tab")
        assert pilot.app.focused.id == "first-element"
        
        await pilot.press("tab")
        assert pilot.app.focused.id == "second-element"
```

### Test Data Binding

```python
async def test_data_updates():
    async with EyeletApp().run_test() as pilot:
        # Change input value
        input_widget = pilot.app.query_one("#my-input")
        input_widget.value = "New value"
        
        # Verify bound data updated
        await pilot.pause()
        assert pilot.app.model.value == "New value"
```

## Tips

1. **Always use `await pilot.pause()`** after navigation or actions that trigger animations
2. **Test both keyboard and mouse interactions** for accessibility
3. **Use meaningful IDs** on widgets for easier testing
4. **Keep tests focused** - one behavior per test
5. **Mock external dependencies** to keep tests fast and reliable
6. **Use snapshot tests** for regression testing of complex UIs
7. **Test error states** not just happy paths
8. **Run tests in different terminal sizes** to ensure responsive design

## Terminal Issues After TUI Exit

If your terminal becomes unresponsive after running the TUI (showing ANSI sequences when typing or mouse movement), the TUI didn't clean up properly.

### Quick Fix

Run the reset script:
```bash
./reset_terminal.sh
```

Or manually reset:
```bash
reset
stty sane
```

### Safe Testing

Use the safe test script which includes cleanup handlers:
```bash
./test_tui_safe.py
```

### What Happens

Textual enables several terminal modes:
- Mouse tracking (captures mouse events)
- Alternate screen buffer
- Raw mode (disables normal key processing)
- Hidden cursor

If the TUI crashes or exits improperly, these modes remain active.

### Prevention

Always use proper exit methods:
- Press `q` or `Ctrl+Q` to quit
- Use the safe test script for development
- Avoid killing the process with Ctrl+C

### Technical Details

The terminal modes that need cleanup:
- `\033[?1000l` - Disable mouse tracking
- `\033[?1003l` - Disable all mouse tracking
- `\033[?1049l` - Exit alternate screen
- `\033[?25h` - Show cursor
- `stty sane` - Reset terminal to sane state

## Resources

- [Textual Testing Documentation](https://textual.textualize.io/guide/testing/)
- [Pytest Async Documentation](https://pytest-asyncio.readthedocs.io/)
- [Example Test Suite](tests/tui/test_app.py)