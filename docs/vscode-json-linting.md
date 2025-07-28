# Setting up JSON Linting for Claude Settings Files

This guide helps you configure VS Code to provide validation and IntelliSense for Claude Code's `settings.json` files.

## Project-Level Configuration (Already Done)

If you're working within the Rigging project, VS Code is already configured to validate Claude settings files. The `.vscode/settings.json` file in this project maps the schema automatically.

## Global VS Code Configuration

To enable validation for Claude settings files in ALL your projects:

1. Open VS Code Settings (JSON):
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Preferences: Open Settings (JSON)"
   - Press Enter

2. Add the following to your settings:

```json
{
  "json.schemas": [
    {
      "fileMatch": [
        "**/claude/settings.json",
        "**/.claude/settings.json"
      ],
      "url": "https://raw.githubusercontent.com/bdmorin/rigging/main/schemas/claude-settings.schema.json"
    }
  ]
}
```

Note: Replace the URL with the actual location once the schema is published.

## Using the Rigging Validate Command

You can also validate Claude settings files using Rigging:

```bash
# Validate current directory's .claude/settings.json
rigging validate settings

# Validate a specific file
rigging validate settings ~/.claude/settings.json

# Validate with a custom schema
rigging validate settings --schema /path/to/schema.json settings.json
```

## Benefits

With JSON schema validation enabled:
- ✅ IntelliSense/autocomplete for hook types and properties
- ✅ Real-time error detection for invalid configurations
- ✅ Hover documentation for configuration options
- ✅ Prevention of common configuration mistakes

## Schema Features

The Claude settings schema validates:
- Hook types (PreToolUse, PostToolUse, etc.)
- Handler types (command, workflow, script)
- Required fields for each hook type
- Matcher patterns for tool hooks
- PreCompact matcher values (manual/auto)

## Example Valid Configuration

```json
{
  "hooks": [
    {
      "type": "PreToolUse",
      "handler": {
        "type": "command",
        "command": "uvx rigging execute --log-only"
      },
      "matcher": ".*"
    },
    {
      "type": "UserPromptSubmit",
      "handler": {
        "type": "command",
        "command": "echo 'User submitted prompt'"
      }
    }
  ]
}
```

## Troubleshooting

If validation isn't working:
1. Ensure VS Code's JSON validation is enabled: `"json.validate.enable": true`
2. Check that the file path matches the patterns in `fileMatch`
3. Verify the schema file is accessible (for local schemas)
4. Reload VS Code window (`Cmd+R` or `Ctrl+R`)