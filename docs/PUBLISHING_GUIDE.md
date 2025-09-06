# Eyelet PyPI Publishing Guide

## Overview

Eyelet uses an automated GitHub Actions workflow to publish releases to PyPI. The process is triggered by creating a GitHub release, which then automatically builds and publishes the package.

## Publishing Method

### 1. Automated Publishing via GitHub Actions

The project uses **two separate workflows** for releases:

1. **`.github/workflows/release.yml`** - Triggered by git tags (v*)
   - Creates GitHub release with changelog
   - Runs tests and quality checks
   - Builds distribution packages
   - Uploads artifacts to GitHub release

2. **`.github/workflows/publish.yml`** - Triggered by GitHub release publication
   - Builds Python packages
   - Publishes to PyPI using TWINE_API_TOKEN

### 2. Step-by-Step Release Process

```bash
# 1. Update version numbers
# Edit pyproject.toml: version = "0.3.6"
# Edit src/eyelet/__init__.py: __version__ = "0.3.6"

# 2. Update CHANGELOG.md
# Add new version section with changes

# 3. Commit changes
git add -A
git commit -m "feat: Release v0.3.6"

# 4. Create annotated tag
git tag -a v0.3.6 -m "Release v0.3.6: Description"

# 5. Push to GitHub with tags
git push origin main --tags
```

### 3. What Happens Next (Automated)

1. **Tag Push Triggers `release.yml`**:
   - Runs tests (pytest, ruff)
   - Builds packages with `uv build`
   - Validates with `twine check`
   - Extracts changelog for this version
   - Creates GitHub release
   - Uploads wheel and source distribution

2. **GitHub Release Triggers `publish.yml`**:
   - Sets up Python 3.11
   - Builds package with `python -m build`
   - Validates with `twine check`
   - Publishes to PyPI using API token

### 4. Required Secrets

The following GitHub secrets must be configured:
- `PYPI_API_TOKEN` - PyPI API token for publishing (set in repository settings)
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

### 5. Manual Publishing (Emergency Only)

If automated publishing fails, you can publish manually:

```bash
# Build the package
uv build

# Check the package
uv run twine check dist/*

# Upload to PyPI (requires TWINE_USERNAME and TWINE_PASSWORD)
TWINE_USERNAME=__token__ TWINE_PASSWORD=<your-pypi-token> \
  twine upload dist/*
```

### 6. Post-Publishing Validation

After publishing, the `.github/workflows/validate-published.yml` workflow can verify:
- Package is available on PyPI
- Installation works correctly
- Basic functionality operates

## Version Management

### Version Locations (Must Update All)
1. `pyproject.toml` - `version = "X.Y.Z"`
2. `src/eyelet/__init__.py` - `__version__ = "X.Y.Z"`
3. `CHANGELOG.md` - Add new version section

### Version Format
- Follow Semantic Versioning: `MAJOR.MINOR.PATCH`
- Use alpha/beta/rc suffixes for pre-releases: `0.4.0-alpha.1`

## Troubleshooting

### Common Issues

1. **Publishing fails with authentication error**
   - Check PYPI_API_TOKEN secret is set correctly
   - Ensure token has upload permissions

2. **GitHub release created but no PyPI upload**
   - Check publish.yml workflow runs
   - Verify release is not marked as draft

3. **Package validation fails**
   - Run `uv build` locally
   - Check with `twine check dist/*`
   - Ensure MANIFEST.in includes all necessary files

### Rollback Procedure

If a bad release is published:

1. **Yank the release on PyPI** (doesn't delete, just marks as yanked):
   ```bash
   # Using twine
   twine yank eyelet==0.3.6
   ```

2. **Create a patch release** with fixes:
   - Increment patch version
   - Follow normal release process

## Best Practices

1. **Always test locally first**:
   ```bash
   mise run test
   mise run lint
   mise run typecheck
   ```

2. **Review the changelog** before releasing

3. **Use descriptive tag messages**

4. **Monitor GitHub Actions** after pushing tags

5. **Verify on PyPI** after publishing:
   ```bash
   uvx eyelet@latest --version
   ```

## GitHub Actions Environment

The publish workflow uses a GitHub Environment named `pypi`:
- URL: https://pypi.org/project/eyelet/
- This allows for deployment protection rules if needed

## Summary

The publishing process is fully automated through GitHub Actions:
1. Developer pushes version tag → GitHub Actions creates release
2. GitHub release published → GitHub Actions publishes to PyPI
3. Users can immediately install with `uvx eyelet@latest`

This ensures consistent, reliable releases with minimal manual intervention.