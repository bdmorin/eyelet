# Eyelet Update Guide

## For uvx Users

When using `uvx`, eyelet runs in an isolated environment. Here's how to ensure you're using the latest version:

### Always Use Latest Version

```bash
# Always fetches the latest version from PyPI
uvx eyelet@latest [command]
```

### Check Current Version

```bash
uvx eyelet --version
```

### Alternative Update Methods

1. **Persistent installation with uv tool**:
```bash
# Install eyelet as a uv tool
uv tool install eyelet@latest

# Force reinstall to update
uv tool install --reinstall eyelet@latest

# Then run commands
eyelet [command]
```

2. **Specify exact version**:
```bash
uvx eyelet@0.3.5  # Replace with desired version
```

3. **Clear cache and run**:
```bash
# Clear the uv cache
uv cache clean

# Run with latest (will re-download)
uvx eyelet@latest [command]
```

### How uvx Works

- `uvx` is an alias for `uv tool run` - it runs tools in isolated environments
- Tools are cached locally in `~/.local/share/uv/tools/`
- Each invocation checks for the specified version
- Using `@latest` ensures you get the newest PyPI release
- There is no `--force` flag for `uvx` - just use `@latest` to get updates

### Troubleshooting Updates

If you're not getting the latest version:

1. **Clear uv cache**:
```bash
uv cache clean
```

2. **Check PyPI for latest version**:
```bash
# See available versions
uv pip index eyelet
```

3. **Use uv tool for persistent installation**:
```bash
# Install/reinstall as a tool
uv tool install --reinstall eyelet@latest
```

## For pipx Users

If you installed with pipx instead:

```bash
# Update to latest
pipx upgrade eyelet

# Or reinstall
pipx reinstall eyelet
```

## For Development Users

If you're running from source with mise:

```bash
# Update dependencies
mise run update

# Or manually with uv
uv sync
```

## Automatic Update Checking

Eyelet includes automatic update checking (can be disabled in settings):

```bash
# Check if updates are available
eyelet version --check-updates

# Disable update checks
eyelet config set auto_update_check false
```

## Version Management Best Practices

1. **Pin versions for CI/CD**:
```bash
uvx eyelet@0.3.4  # Specific version for reproducibility
```

2. **Use latest for interactive work**:
```bash
uvx eyelet@latest  # Always get newest features
```

3. **Check changelog before major updates**:
```bash
# View changelog online
eyelet docs --changelog
```

## Notes on uv/uvx Behavior

- `uvx` is essentially `uv tool run` - it runs tools in isolated environments
- Tools are cached, so `@latest` might use cached version unless forced
- The `--force` flag ensures a fresh installation
- Each tool gets its own virtual environment with locked dependencies
- Updates are intentionally explicit to avoid breaking changes

## Integration with mise

For projects using mise, you can configure eyelet as a tool:

```toml
# mise.toml or .mise.toml
[tools]
python = "3.11"
"pipx:eyelet" = "latest"  # Or specific version like "0.3.4"
```

Then use:
```bash
mise install  # Install/update all tools
mise run eyelet -- [command]  # Run eyelet
```