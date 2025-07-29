#!/bin/bash
# Manual PyPI Publishing Script
# Based on pytruststore's publishing approach

set -e  # Exit on error

echo "🚀 Eyelet PyPI Publishing Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Are you in the project root?"
    exit 1
fi

# Get current version
VERSION=$(grep -E "^version = " pyproject.toml | cut -d'"' -f2)
echo "📦 Current version: $VERSION"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Build the package
echo "🔨 Building package..."
python -m build

# Check the package
echo "✅ Checking package with twine..."
twine check dist/*

# Upload to PyPI
echo "📤 Uploading to PyPI..."
echo "   (You'll need your PyPI token)"
echo "   Username: __token__"
echo "   Password: Your PyPI token (pypi-...)"
echo ""

# Set non-interactive mode for automation
export TWINE_NON_INTERACTIVE=1

# Upload with verbose output
twine upload --verbose dist/*

echo "✨ Done! Package published to PyPI"
echo "🔗 View at: https://pypi.org/project/eyelet/$VERSION/"