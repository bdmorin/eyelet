# Eyelet TUI Interactions

## Overview
The Eyelet TUI provides a comprehensive interface for managing Claude Code hooks with a nautical theme and Catppuccin color schemes.

## Main Menu
- **Configure Hooks** - Manage hook configurations
- **Browse Templates** - View and install hook templates  
- **View Logs** - Browse and search hook execution logs
- **Discover Hooks** - Find hooks from Git history and examples
- **Settings** - Application settings and preferences
- **Help** - Documentation and keyboard shortcuts

## Detailed Interactions

### 1. Configure Hooks Screen
**Purpose**: Manage Claude Code hook configurations

#### Sub-screens:
- **Hook List View**
  - List all configured hooks (from .claude/settings.json)
  - Show hook type, handler type, and matcher
  - Color coding: PreToolUse (blue), PostToolUse (green), etc.
  - Actions: Add, Edit, Delete, Toggle Enable/Disable
  - Quick filter by hook type

- **Hook Editor**
  - Hook type selector (dropdown)
  - Matcher input with regex validation
  - Handler type selector (command/workflow/script)
  - Handler configuration (command line, script content)
  - Test hook button
  - Save/Cancel buttons

- **Quick Actions**
  - Install universal logging (one-click)
  - Enable/disable all hooks
  - Import/export hooks

### 2. Browse Templates Screen
**Purpose**: Discover and install hook templates

#### Features:
- **Template Grid/List View**
  - Template cards with name, description, category
  - Category filters: Security, Monitoring, Development, Custom
  - Search by name or description
  - Preview template details

- **Template Details View**
  - Full template description
  - Hook configurations preview
  - Variables required
  - Install button with variable input dialog
  - Copy to clipboard option

- **Template Management**
  - Create new template from current hooks
  - Edit custom templates
  - Share template (export)
  - Import template from file/URL

### 3. View Logs Screen
**Purpose**: Browse and analyze hook execution logs

#### Views:
- **Log Timeline**
  - Chronological list of hook executions
  - Compact view: timestamp, hook type, tool, status
  - Expandable rows for full details
  - Color coding: success (green), error (red), blocked (yellow)
  - Real-time updates

- **Log Search**
  - Full-text search across logs
  - Filter by:
    - Date range
    - Hook type
    - Tool name
    - Status (success/error/blocked)
    - Session ID
  - Save search queries

- **Log Analytics**
  - Summary statistics
  - Error frequency chart
  - Most active hooks
  - Performance metrics
  - Export options (JSON, CSV)

### 4. Discover Hooks Screen
**Purpose**: Find hook ideas and configurations

#### Sections:
- **Git History Scanner**
  - Scan Git history for hook patterns
  - Extract hook configurations from commits
  - Preview found hooks
  - Quick install button

- **Example Browser**
  - Categorized examples
  - Use case descriptions
  - Copy configuration
  - Adapt to current project

- **Community Hooks**
  - Browse shared hooks (future feature)
  - Rate and comment
  - Fork and customize

### 5. Settings Screen
**Purpose**: Configure Eyelet and theme preferences

#### Categories:
- **Appearance**
  - Theme selector (Mocha/Latte)
  - Font size adjustment
  - Compact/comfortable view mode
  - Animations on/off

- **Logging Configuration**
  - Log format (JSON/SQLite/Both)
  - Log retention period
  - Log file locations
  - Performance settings

- **Claude Integration**
  - Claude settings path
  - Hook execution timeout
  - Error handling behavior
  - Debug mode toggle

- **Advanced**
  - Export/import all settings
  - Reset to defaults
  - Clear cache/logs
  - System info

### 6. Help Screen
**Purpose**: In-app documentation and assistance

#### Content:
- **Quick Start Guide**
  - Interactive tutorial
  - Key concepts
  - Common workflows

- **Keyboard Shortcuts**
  - Global shortcuts
  - Screen-specific shortcuts
  - Customizable bindings

- **Troubleshooting**
  - Common issues
  - Diagnostic tools
  - Report issue button

- **About**
  - Version info
  - Credits
  - License
  - Check for updates

## Global Features

### Navigation
- **Tab/Shift+Tab**: Navigate between elements
- **Enter**: Select/activate
- **Escape**: Go back/cancel
- **Ctrl+Q**: Quit application
- **F1**: Context help
- **Ctrl+S**: Quick save (context sensitive)

### Status Bar
- Current screen/mode
- Hook execution status (if running)
- Notification count
- Clock
- Quick actions

### Notifications
- Toast notifications for:
  - Hook execution results
  - Errors and warnings
  - Background task completion
- Notification center (Ctrl+N)

### Command Palette
- **Ctrl+P**: Open command palette
- Fuzzy search all actions
- Recent commands
- Custom command shortcuts

## Implementation Priority

1. **Phase 1 - Core Functionality**
   - Main menu
   - Configure Hooks (basic list and edit)
   - View Logs (basic timeline)
   - Settings (theme selector)

2. **Phase 2 - Enhanced Features**
   - Templates browser
   - Log search and filters
   - Hook editor improvements
   - Help system

3. **Phase 3 - Advanced Features**
   - Discover hooks
   - Analytics dashboard
   - Command palette
   - Community features

## Technical Considerations

### State Management
- Hook configurations
- User preferences
- Log cache
- Search history
- UI state (selected items, scroll positions)

### Performance
- Lazy loading for logs
- Virtual scrolling for large lists
- Background log indexing
- Debounced search

### Error Handling
- Graceful degradation
- User-friendly error messages
- Retry mechanisms
- Fallback to CLI