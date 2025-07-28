# Publishing Rigging to PyPI

This guide walks through the steps to publish Rigging to PyPI so it can be used with `uvx rigging`.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org
2. **API Token**: Generate an API token at https://pypi.org/manage/account/token/
   - Scope: Entire account (for first publish) or project-specific (after first publish)
3. **Test PyPI Account** (optional): Create account at https://test.pypi.org for testing

## First-Time Setup

### 1. Verify Package Name Availability

```bash
# Check if 'rigging' is available (we already verified it is!)
pip search rigging
```

### 2. Configure GitHub Secrets

Add your PyPI API token to GitHub:
1. Go to Settings → Secrets and variables → Actions
2. Add new repository secret: `PYPI_API_TOKEN`
3. Paste your PyPI API token

### 3. Test Build Locally

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
uv build

# Check the package
pip install twine
twine check dist/*
```

## Publishing Process

### Option 1: Manual Publishing (First Time)

```bash
# Build the package
uv build

# Upload to Test PyPI first (optional)
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ rigging

# Upload to PyPI
twine upload dist/*
```

### Option 2: GitHub Release (Recommended)

1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a new release on GitHub:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
4. Go to GitHub → Releases → Create new release
5. Choose the tag, add release notes
6. Publish release (this triggers the publish workflow)

## Post-Publishing Verification

```bash
# Wait a few minutes for PyPI to update, then test:
uvx rigging --version
uvx rigging validate settings
uvx rigging configure install-all --help
```

## Version Management

- Use semantic versioning: MAJOR.MINOR.PATCH
- Update version in `pyproject.toml` before each release
- Tag releases with `v` prefix: `v0.1.0`, `v0.2.0`, etc.

## Troubleshooting

### Package Name Conflicts
If 'rigging' becomes unavailable, alternative names:
- `rigging-ai`
- `claude-rigging`
- `hook-rigging`

### Build Issues
```bash
# Clear all build artifacts
rm -rf dist/ build/ src/*.egg-info
uv cache clean
uv build
```

### Upload Failures
- Check your API token is valid
- Ensure version number hasn't been used before
- Verify all metadata in pyproject.toml

## Security Notes

- Never commit your PyPI API token
- Use GitHub secrets for automation
- Consider using a project-specific token after first publish
- Enable 2FA on your PyPI account