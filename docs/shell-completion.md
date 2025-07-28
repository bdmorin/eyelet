# Shell Completion Guide for Rigging

Shell completion enables tab-completion for Rigging commands, options, and arguments in your terminal. This greatly improves the command-line experience by reducing typing and helping discover available options.

## Quick Start

```bash
# Auto-detect and install for your current shell
rigging completion install

# Or install for a specific shell
rigging completion install bash
rigging completion install zsh
rigging completion install fish
rigging completion install powershell
```

## Supported Shells

### Bash

For Bash, completion is installed to one of these locations:
- `~/.bash_completion.d/rigging`
- `/etc/bash_completion.d/rigging`
- `~/.rigging-completion.bash` (fallback)

After installation, add this to your `~/.bashrc`:
```bash
source ~/.bash_completion.d/rigging  # Or wherever it was installed
```

### Zsh

For Zsh, completion is installed to:
- `~/.zsh/completions/_rigging`
- `~/.config/zsh/completions/_rigging`
- `~/.rigging-completion.zsh` (fallback)

Add to your `~/.zshrc`:
```bash
source ~/.zsh/completions/_rigging  # Or wherever it was installed
```

### Fish

For Fish, completion is automatically loaded from:
- `~/.config/fish/completions/rigging.fish`

No additional configuration needed!

### PowerShell

For PowerShell, add to your profile:
```powershell
. ~/.rigging-completion.ps1
```

## Features

### Command Completion
```bash
rigging <TAB>
# Shows: configure, template, logs, execute, discover, completion, help, tui
```

### Subcommand Completion
```bash
rigging configure <TAB>
# Shows: list, add, remove, enable, disable, clear
```

### Option Completion
```bash
rigging logs --<TAB>
# Shows: --tail, --hook-type, --tool, --status, --json, --details, --follow
```

### Dynamic Value Completion
```bash
rigging logs --hook-type <TAB>
# Shows: PreToolUse, PostToolUse, Notification, UserPromptSubmit, Stop, SubagentStop, PreCompact

rigging logs --tool <TAB>
# Shows: Bash, Glob, Grep, Read, Edit, Write, WebFetch, WebSearch, Task
```

### File/Directory Completion
```bash
rigging template import <TAB>
# Shows: Files in current directory

rigging --config-dir <TAB>
# Shows: Directories only
```

## Management Commands

### Check Installation Status
```bash
rigging completion status
```

### View Completion Script
```bash
rigging completion show bash
rigging completion show zsh
```

### Custom Installation Path
```bash
rigging completion install --path /custom/path/completions/
```

## Troubleshooting

### Completion Not Working

1. **Ensure the script is sourced:**
   ```bash
   # For bash/zsh
   source ~/.bashrc  # or ~/.zshrc
   ```

2. **Check if completion is loaded:**
   ```bash
   # Bash
   complete -p | grep rigging
   
   # Zsh
   print -l ${(ok)_comps} | grep rigging
   ```

3. **Verify installation:**
   ```bash
   rigging completion status
   ```

### Permission Issues

If you get permission errors during installation:
```bash
# Install to user directory
rigging completion install --path ~/.local/share/bash-completion/completions/
```

### Updating Completion

When Rigging is updated, reinstall completion to get new commands:
```bash
rigging completion install --force
```

## Advanced Usage

### Custom Completion Functions

You can extend Rigging's completion by adding custom functions:

```bash
# Bash example
_rigging_custom() {
    # Your custom completion logic
    COMPREPLY+=("custom-option")
}

# Hook into Rigging's completion
complete -F _rigging_completion -o nosort rigging
```

### Completion for Aliases

If you create aliases for Rigging:
```bash
alias rig='rigging'

# Bash
complete -F _rigging_completion -o nosort rig

# Zsh
compdef _rigging_completion rig
```

## Environment Variables

Rigging's completion respects these environment variables:
- `RIGGING_COMPLETE_DEBUG` - Enable debug output
- `RIGGING_COMPLETE_CACHE` - Cache completion results (faster but may be stale)

## Contributing

To improve shell completion:
1. Edit completion scripts in `src/rigging/cli/completion.py`
2. Test with all supported shells
3. Update this documentation
4. Submit a pull request

## Future Enhancements

Planned improvements:
- Context-aware completion (e.g., only show valid matchers for hook type)
- Fuzzy matching support
- Integration with Fig, Warp, and other modern terminals
- Completion for workflow names and template IDs