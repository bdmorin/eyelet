# PyPI Publishing Guide for Eyelet

This guide explains how to publish Eyelet to the Python Package Index (PyPI).

## Overview

Eyelet uses GitHub Actions for automated publishing when a new release is created. The workflow is based on the proven setup from pytruststore.

## Automated Publishing (Recommended)

### Prerequisites

1. PyPI account with API token
2. API token added to GitHub repository secrets as `PYPI_API_TOKEN`

### Publishing Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Commit and push** changes:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

4. **Create and push tag**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. **Create GitHub release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes "See CHANGELOG.md"
   ```

The GitHub Actions workflow will automatically:
- Build the package
- Check package integrity
- Upload to PyPI with verbose logging

## Manual Publishing

If you need to publish manually:

```bash
# Use the provided script
./scripts/publish_to_pypi.sh

# Or manually:
python -m build
twine check dist/*
twine upload --verbose dist/*
```

## Environment Variables

The workflow uses these environment variables:
- `TWINE_USERNAME`: Set to `__token__`
- `TWINE_PASSWORD`: Your PyPI API token
- `TWINE_NON_INTERACTIVE`: Set to `1` for automation

## Troubleshooting

### "File already exists" Error
You cannot overwrite existing versions on PyPI. Increment the version number.

### Authentication Failed
1. Check your API token is correct
2. Ensure username is `__token__` (not your PyPI username)
3. Verify the token has upload permissions

### Build Failures
1. Test locally: `python -m build`
2. Check `pyproject.toml` syntax
3. Ensure all files are included in the package

## Testing Before Release

```bash
# Build locally
python -m build

# Install and test
pip install dist/eyelet-*.whl
eyelet --version
```

## Version Numbering

Follow semantic versioning:
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes (backwards compatible)

## Checklist

- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Git tag created
- [ ] GitHub release created