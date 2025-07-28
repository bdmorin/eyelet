# Publishing to PyPI - Quick Guide

## Option 1: Manual Publishing (Fastest)

Since you need to test `uvx --from rigging-cli rigging` immediately, let's publish manually:

### 1. Install twine
```bash
pip install twine
```

### 2. Create PyPI Account (if you haven't)
- Go to https://pypi.org/account/register/
- Verify your email
- Go to https://pypi.org/manage/account/
- Add 2FA (recommended)

### 3. Create API Token
- Go to https://pypi.org/manage/account/token/
- Token name: "rigging-initial"
- Scope: "Entire account" (for first upload)
- Copy the token (starts with `pypi-`)

### 4. Configure twine
Create ~/.pypirc:
```ini
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
```

### 5. Upload to PyPI
```bash
cd /Users/bdmorin/src/claude-hooks
twine upload dist/*
```

### 6. Test immediately
```bash
# Wait 1-2 minutes for PyPI to update
uvx --from rigging-cli rigging --version
uvx --from rigging-cli rigging validate settings
```

## Option 2: Test on TestPyPI First (Safer)

If you want to test first:

1. Create account at https://test.pypi.org
2. Get token from https://test.pypi.org/manage/account/token/
3. Upload: `twine upload --repository testpypi dist/*`
4. Test: `pip install --index-url https://test.pypi.org/simple/ rigging`

## Option 3: GitHub Release (Automated)

1. Add your PyPI token to GitHub secrets (PYPI_API_TOKEN)
2. Add the workflow files from `workflows-to-add/`
3. Create a release on GitHub
4. It will auto-publish

## Verification

Once published:
```bash
# Should work globally now!
uvx --from rigging-cli rigging validate settings
uvx --from rigging-cli rigging configure install-all
uvx --from rigging-cli rigging --help
```

The 'rigging' name is available on PyPI, so you're good to go!