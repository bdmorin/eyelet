# Eyelet Template Library

Templates are pre-configured hook collections that solve common automation needs. Like a ship's armory stocked with proven weapons, Eyelet's template library provides battle-tested configurations ready for deployment.

## Table of Contents
- [Overview](#overview)
- [Available Templates](#available-templates)
- [Using Templates](#using-templates)
- [Template Structure](#template-structure)
- [Creating Custom Templates](#creating-custom-templates)
- [Sharing Templates](#sharing-templates)
- [Example Templates](#example-templates)
- [Best Practices](#best-practices)

## Overview

Eyelet templates are curated collections of hooks designed to work together for specific use cases. They provide:

- **Quick deployment** - Install complete hook configurations with a single command
- **Parameterization** - Customize templates with variables during installation
- **Version control** - Track template versions and updates
- **Community sharing** - Export and share templates with other users

Templates are deployed into action to configure your hooks.

## Available Templates

### Built-in Template Categories

#### 🛡️ Security Templates
Protect your development environment from dangerous operations.

- **safety-check** - Prevents dangerous commands from executing
  - Blocks `rm -rf /`, fork bombs, and pipe-to-shell attacks
  - Validates file paths and operations
  - Customizable dangerous pattern matching

#### 📊 Monitoring Templates
Track and analyze Claude Code's behavior.

- **logger** - Universal logging for all tool usage
  - Tracks command history and performance
  - Structured JSON logging with daily rotation
  - Configurable output locations

#### 🔧 Development Workflow Templates
Enhance your development processes.

- **enhancer** - Output enhancement and formatting
  - Formats command outputs for readability
  - Filters sensitive information
  - Adds metadata and annotations

- **workflow** - Multi-step workflow coordination
  - Sequential task execution
  - Conditional logic based on results
  - State persistence between steps

## Using Templates

### List Available Templates

```bash
# View all templates in your armory
eyelet template list

# Filter by category
eyelet template list --category security
```

### View Template Details

```bash
# Inspect the ordinance
eyelet template show logger
```

Output shows:
- Template metadata (name, author, version)
- Hook configurations
- Required variables
- Example use cases

### Install a Template

```bash
# Load the cannons! (Install to project)
eyelet template install safety-check

# Install to user configuration
eyelet template install logger --scope user

# Install with custom variables
eyelet template install logger --var log_location=/var/log/claude-hooks
```

During installation, Eyelet will:
1. Prompt for any required variables not provided
2. Apply variable substitution to hook configurations
3. Add hooks to your configuration
4. Report successful deployment

### Export a Template

```bash
# Share the wealth
eyelet template export my-custom-template ./my-template.json
```

### Import a Template

```bash
# Bring aboard new ordinance
eyelet template import ./downloaded-template.json
```

## Template Structure

Templates are JSON files with the following structure:

```json
{
  "id": "safety-check",
  "name": "Safety Check Hook",
  "description": "Prevents dangerous commands from executing",
  "category": "security",
  "version": "1.0.0",
  "author": "Eyelet Team",
  "tags": ["safety", "bash", "security"],
  "variables": {
    "dangerous_patterns": [
      "rm -rf /",
      ":(){ :|:& };:"
    ],
    "block_message": "Command blocked for safety"
  },
  "hooks": [
    {
      "id": "block-dangerous-commands",
      "type": "PreToolUse",
      "enabled": true,
      "description": "Block dangerous bash commands",
      "matcher": {
        "type": "tool",
        "pattern": "Bash"
      },
      "handler": {
        "type": "script",
        "path": "~/.eyelet/handlers/safety-check.py"
      }
    }
  ]
}
```

### Template Fields

- **id**: Unique identifier (lowercase, no spaces)
- **name**: Human-readable name
- **description**: What the template does
- **category**: Template category (security, monitoring, development, testing, custom)
- **version**: Semantic version number
- **author**: Template creator (optional)
- **tags**: Searchable tags (optional)
- **variables**: Configurable parameters with defaults
- **hooks**: Array of hook configurations

## Creating Custom Templates

### Interactive Creation

```bash
# Forge new weapons
eyelet template create
```

The interactive wizard will guide you through:
1. Basic template information
2. Variable definitions
3. Hook configurations
4. Testing and validation

### Manual Template Creation

Create a JSON file following the template structure:

```json
{
  "id": "git-workflow",
  "name": "Git Workflow Automation",
  "description": "Automate git operations with safety checks",
  "category": "development",
  "version": "1.0.0",
  "variables": {
    "auto_commit": true,
    "commit_prefix": "[AUTO]"
  },
  "hooks": [
    {
      "id": "pre-commit-check",
      "type": "PreToolUse",
      "enabled": true,
      "matcher": {
        "type": "tool",
        "pattern": "Bash"
      },
      "handler": {
        "type": "inline",
        "code": "# Check for git operations\nif [[ $TOOL_INPUT == *\"git commit\"* ]]; then\n  echo \"Validating commit...\"\nfi"
      }
    }
  ]
}
```

### Template Variables

Variables allow customization during installation:

```json
"variables": {
  "log_dir": "~/.eyelet/logs",          // String with default
  "max_file_size": 1048576,             // Number (1MB)
  "enable_filtering": true,             // Boolean
  "allowed_commands": ["ls", "cat"]     // Array
}
```

Variables are replaced in:
- Hook handler paths
- Inline script code
- Configuration values
- Matcher patterns

## Sharing Templates

### Community Templates

Share your templates with the Eyelet community:

1. **Export your template**:
   ```bash
   eyelet template export my-awesome-template ./my-template.json
   ```

2. **Test thoroughly**:
   - Install in a clean environment
   - Verify all hooks work correctly
   - Document any prerequisites

3. **Share via**:
   - GitHub repositories
   - Gist snippets
   - Community forums
   - Pull requests to official templates

### Template Repository Structure

For sharing multiple templates:

```
my-eyelet-templates/
├── README.md
├── templates/
│   ├── security/
│   │   ├── enhanced-safety.json
│   │   └── audit-logger.json
│   ├── development/
│   │   ├── pr-automation.json
│   │   └── test-runner.json
│   └── monitoring/
│       └── performance-tracker.json
└── handlers/
    ├── enhanced-safety.py
    └── pr-automation.sh
```

## Example Templates

### 1. Universal Logging Template

Complete template for comprehensive logging:

```json
{
  "id": "universal-logger",
  "name": "Universal Logging System",
  "description": "Log all Claude Code interactions with structured output",
  "category": "monitoring",
  "version": "2.0.0",
  "author": "Eyelet Team",
  "tags": ["logging", "monitoring", "analytics"],
  "variables": {
    "log_directory": "~/.eyelet/logs",
    "log_format": "jsonl",
    "include_context": true,
    "rotation_days": 7
  },
  "hooks": [
    {
      "id": "pre-tool-logger",
      "type": "PreToolUse",
      "enabled": true,
      "description": "Log tool invocations",
      "handler": {
        "type": "script",
        "path": "~/.eyelet/handlers/universal-logger.py",
        "args": ["--pre", "--dir", "{{log_directory}}"]
      }
    },
    {
      "id": "post-tool-logger",
      "type": "PostToolUse",
      "enabled": true,
      "description": "Log tool results",
      "handler": {
        "type": "script",
        "path": "~/.eyelet/handlers/universal-logger.py",
        "args": ["--post", "--dir", "{{log_directory}}"]
      }
    }
  ]
}
```

Handler script (`universal-logger.py`):

```python
#!/usr/bin/env python3
"""Universal logging handler for Eyelet"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pre', action='store_true')
    parser.add_argument('--post', action='store_true')
    parser.add_argument('--dir', default='~/.eyelet/logs')
    args = parser.parse_args()
    
    # Read hook input
    input_data = json.load(sys.stdin)
    
    # Create log entry
    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'hook_type': 'PreToolUse' if args.pre else 'PostToolUse',
        'tool_name': input_data.get('tool_name'),
        'tool_input': input_data.get('tool_input'),
        'context': input_data.get('context', {})
    }
    
    # Write to log file
    log_dir = Path(args.dir).expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{datetime.now():%Y-%m-%d}.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Allow execution
    sys.exit(0)

if __name__ == '__main__':
    main()
```

### 2. Git Hooks Integration Template

Integrate with git pre-commit hooks:

```json
{
  "id": "git-integration",
  "name": "Git Hooks Integration",
  "description": "Validate and enhance git operations",
  "category": "development",
  "version": "1.0.0",
  "variables": {
    "check_branch": true,
    "protected_branches": ["main", "master", "production"],
    "require_issue_number": true
  },
  "hooks": [
    {
      "id": "git-commit-validator",
      "type": "PreToolUse",
      "enabled": true,
      "matcher": {
        "type": "tool",
        "pattern": "Bash"
      },
      "handler": {
        "type": "inline",
        "code": "#!/bin/bash\n# Validate git commits\nif [[ \"$TOOL_INPUT\" =~ git\\ commit ]]; then\n  BRANCH=$(git branch --show-current)\n  if [[ \" {{protected_branches}} \" =~ \" $BRANCH \" ]]; then\n    echo \"Error: Cannot commit directly to $BRANCH\" >&2\n    exit 2\n  fi\nfi\nexit 0"
      }
    }
  ]
}
```

### 3. Security Scanning Template

Automated security checks:

```json
{
  "id": "security-scanner",
  "name": "Security Scanner",
  "description": "Scan for security issues in code operations",
  "category": "security",
  "version": "1.2.0",
  "tags": ["security", "scanning", "secrets"],
  "variables": {
    "scan_patterns": [
      "password\\s*=",
      "api[_-]?key\\s*=",
      "secret\\s*=",
      "token\\s*="
    ],
    "scan_extensions": [".py", ".js", ".env", ".config"]
  },
  "hooks": [
    {
      "id": "secret-scanner",
      "type": "PreToolUse",
      "enabled": true,
      "matcher": {
        "type": "tool",
        "pattern": "Write|Edit"
      },
      "handler": {
        "type": "script",
        "path": "~/.eyelet/handlers/secret-scanner.py"
      }
    }
  ]
}
```

### 4. Code Quality Template

Enforce code quality standards:

```json
{
  "id": "code-quality",
  "name": "Code Quality Enforcer",
  "description": "Run linters and formatters automatically",
  "category": "development",
  "version": "1.0.0",
  "variables": {
    "python_formatter": "black",
    "js_linter": "eslint",
    "auto_fix": true
  },
  "hooks": [
    {
      "id": "python-formatter",
      "type": "PostToolUse",
      "enabled": true,
      "matcher": {
        "type": "and",
        "conditions": [
          {"type": "tool", "pattern": "Write|Edit"},
          {"type": "path", "pattern": ".*\\.py$"}
        ]
      },
      "handler": {
        "type": "command",
        "command": "{{python_formatter}} {{file_path}}"
      }
    }
  ]
}
```

## Best Practices

### Template Design

1. **Single Responsibility**: Each template should solve one specific problem well
2. **Sensible Defaults**: Provide good default values for variables
3. **Clear Documentation**: Include detailed descriptions and examples
4. **Version Control**: Use semantic versioning for template updates
5. **Error Handling**: Templates should fail gracefully with helpful messages

### Variable Naming

- Use descriptive names: `log_directory` not `dir`
- Follow naming conventions: `snake_case` for variables
- Group related variables with prefixes: `git_check_branch`, `git_protected_branches`

### Hook Organization

- Order hooks by execution phase (Pre before Post)
- Group related hooks together
- Use consistent naming patterns for hook IDs
- Include clear descriptions for each hook

### Testing Templates

Before sharing:

1. Test in isolation with minimal configuration
2. Test with various variable combinations
3. Verify error handling for edge cases
4. Document any system requirements
5. Include example usage in documentation

### Security Considerations

- Never include sensitive data in templates
- Use variables for paths and credentials
- Validate all user inputs in handlers
- Prefer fail-open for safety-critical hooks
- Document security implications clearly

### Performance Tips

- Keep handlers lightweight and fast
- Use appropriate matchers to minimize overhead
- Cache expensive operations when possible
- Log asynchronously for high-volume hooks
- Monitor resource usage of installed templates

## Template Development Workflow

1. **Identify the need**: What problem does this template solve?
2. **Design the solution**: Which hooks and handlers are needed?
3. **Create minimal version**: Start with basic functionality
4. **Test thoroughly**: Install and verify behavior
5. **Add variables**: Make it customizable
6. **Document usage**: Include examples and edge cases
7. **Share with community**: Export and publish

Remember: Good templates are like well-maintained weapons in a ship's armory - reliable, tested, and ready for action when needed!