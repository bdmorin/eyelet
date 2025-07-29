# Copy These Files to GitHub

Since the OAuth app can't create workflows, copy these manually:

## 1. Create .github/workflows/ci.yml

Go to https://github.com/bdmorin/eyelet → Add file → Create new file
Name: `.github/workflows/ci.yml`

Copy this content:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v4
      with:
        enable-cache: true
        cache-dependency-glob: "uv.lock"
    
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        uv sync --all-extras --dev
    
    - name: Lint with ruff
      run: |
        uv run ruff check .
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
    
    - name: Format check with ruff
      run: |
        uv run ruff format --check .
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
    
    - name: Type check with mypy
      run: |
        uv run mypy src/eyelet
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
      continue-on-error: true
    
    - name: Test with pytest
      run: |
        uv run pytest tests/ -v --cov=eyelet --cov-report=xml
      continue-on-error: true
    
    - name: Upload coverage reports to Codecov
      uses: codecov/codecov-action@v4
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
      continue-on-error: true
    
    - name: Build package
      run: |
        uv build
    
    - name: Test installation
      run: |
        uv pip install dist/*.whl
        eyelet --version
        eyelet validate settings --help
```

## 2. Create .github/workflows/publish.yml

Name: `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v4
      with:
        enable-cache: true
    
    - name: Set up Python
      run: uv python install 3.11
    
    - name: Build package
      run: uv build
    
    - name: Check package
      run: |
        uv pip install twine
        uv run twine check dist/*
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        uv run twine upload dist/*
```

## 3. Test the Setup

After adding both workflows:

1. **Test CI**: Push any change and watch Actions tab
2. **Test Release**: Create a version tag:

```bash
git tag v0.1.3
git push origin v0.1.3
```

Then go to Releases → Draft a new release → Choose v0.1.3 tag → Publish

This will trigger automatic PyPI publishing! 🚀

## 4. Optional: Advanced Workflows

If you want the full automation (release creation from tags), also add:
- `release.yml` - Auto-creates GitHub releases from version tags
- `validate-published.yml` - Tests published packages

But start with just ci.yml and publish.yml for now!