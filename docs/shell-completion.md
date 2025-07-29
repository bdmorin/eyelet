# Shell Completion Guide for Eyelet

Shell completion enables tab-completion for Eyelet commands, options, and arguments in your terminal. This greatly improves the command-line experience by reducing typing and helping discover available options.

## Quick Start

```bash
# Auto-detect and install for your current shell
uvx --from eyelet eyelet completion install

# Or install for a specific shell
uvx --from eyelet eyelet completion install bash
uvx --from eyelet eyelet completion install zsh
uvx --from eyelet eyelet completion install fish
uvx --from eyelet eyelet completion install powershell
```

## Supported Shells

### Bash

For Bash, completion is installed to one of these locations:
- `~/.bash_completion.d/eyelet`
- `/etc/bash_completion.d/eyelet`
- `~/.eyelet-completion.bash` (fallback)

After installation, add this to your `~/.bashrc`:
```bash
source ~/.bash_completion.d/eyelet  # Or wherever it was installed
```

### Zsh

For Zsh, completion is installed to:
- `~/.zsh/completions/_eyelet`
- `~/.config/zsh/completions/_eyelet`
- `~/.eyelet-completion.zsh` (fallback)

Add to your `~/.zshrc`:
```bash
source ~/.zsh/completions/_eyelet  # Or wherever it was installed
```

### Fish

For Fish, completion is automatically loaded from:
- `~/.config/fish/completions/eyelet.fish`

No additional configuration needed!

### PowerShell

For PowerShell, add to your profile:
```powershell
. ~/.eyelet-completion.ps1
```

## Features

### Command Completion
```bash
uvx --from eyelet eyelet <TAB>
# Shows: configure, template, logs, execute, discover, completion, help, tui
```

### Subcommand Completion
```bash
uvx --from eyelet eyelet configure <TAB>
# Shows: list, add, remove, enable, disable, clear
```

### Option Completion
```bash
uvx --from eyelet eyelet logs --<TAB>
# Shows: --tail, --hook-type, --tool, --status, --json, --details, --follow
```

### Dynamic Value Completion
```bash
uvx --from eyelet eyelet logs --hook-type <TAB>
# Shows: PreToolUse, PostToolUse, Notification, UserPromptSubmit, Stop, SubagentStop, PreCompact

uvx --from eyelet eyelet logs --tool <TAB>
# Shows: Bash, Glob, Grep, Read, Edit, Write, WebFetch, WebSearch, Task
```

### File/Directory Completion
```bash
uvx --from eyelet eyelet template import <TAB>
# Shows: Files in current directory

eyelet --config-dir <TAB>
# Shows: Directories only
```

## Management Commands

### Check Installation Status
```bash
uvx --from eyelet eyelet completion status
```

### View Completion Script
```bash
uvx --from eyelet eyelet completion show bash
uvx --from eyelet eyelet completion show zsh
```

### Custom Installation Path
```bash
uvx --from eyelet eyelet completion install --path /custom/path/completions/
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
   complete -p | grep eyelet
   
   # Zsh
   print -l ${(ok)_comps} | grep eyelet
   ```

3. **Verify installation:**
   ```bash
   uvx --from eyelet eyelet completion status
   ```

### Permission Issues

If you get permission errors during installation:
```bash
# Install to user directory
uvx --from eyelet eyelet completion install --path ~/.local/share/bash-completion/completions/
```

### Updating Completion

When Eyelet is updated, reinstall completion to get new commands:
```bash
uvx --from eyelet eyelet completion install --force
```

## Advanced Usage

### Custom Completion Functions

You can extend Eyelet's completion by adding custom functions:

```bash
# Bash example
_eyelet_custom() {
    # Your custom completion logic
    COMPREPLY+=("custom-option")
}

# Hook into Eyelet's completion
complete -F _eyelet_completion -o nosort eyelet
```

### Completion for Aliases

If you create aliases for Eyelet:
```bash
alias rig='eyelet'

# Bash
complete -F _eyelet_completion -o nosort rig

# Zsh
compdef _eyelet_completion rig
```

## Environment Variables

Eyelet's completion respects these environment variables:
- `RIGGING_COMPLETE_DEBUG` - Enable debug output
- `RIGGING_COMPLETE_CACHE` - Cache completion results (faster but may be stale)

## Contributing

To improve shell completion:
1. Edit completion scripts in `src/eyelet/cli/completion.py`
2. Test with all supported shells
3. Update this documentation
4. Submit a pull request

## Future Enhancements

Planned improvements:
- Context-aware completion (e.g., only show valid matchers for hook type)
- Fuzzy matching support
- Integration with Fig, Warp, and other modern terminals
- Completion for workflow names and template IDs