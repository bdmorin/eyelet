# Setting up GitHub Repository

## Quick Start

1. **Create the repository on GitHub**:
   ```bash
   gh repo create eyelet --public --description "Hook orchestration system for AI agents - All hands to the eyelet!"
   ```
   
   Or manually at: https://github.com/new
   - Repository name: `eyelet`
   - Description: "Hook orchestration system for AI agents - All hands to the eyelet!"
   - Public repository
   - Don't initialize with README (we have one)

2. **Push your code**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Eyelet - Hook orchestration for Claude Code"
   git branch -M main
   git remote add origin https://github.com/bdmorin/eyelet.git
   git push -u origin main
   ```

3. **Set up GitHub Pages** (optional, for docs):
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: main / docs folder

4. **Configure repository settings**:
   - Go to Settings → General
   - Features: Enable Issues, Discussions
   - Add topics: `claude-code`, `hooks`, `ai`, `automation`, `python`, `uvx`

5. **Add PyPI secret**:
   - Go to Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: (your PyPI API token)

## What's Included

- ✅ MIT License
- ✅ Comprehensive README
- ✅ Contributing guidelines
- ✅ GitHub Actions for CI/CD
- ✅ Publishing workflow for PyPI
- ✅ .gitignore configured
- ✅ Documentation

## Next Steps

1. Push to GitHub
2. Create first release (v0.1.0)
3. This will trigger PyPI publication
4. Then `uvx eyelet` will work globally!

## Manual PyPI Publishing (if needed)

```bash
# Build
uv build

# Check
twine check dist/*

# Upload
twine upload dist/*
```