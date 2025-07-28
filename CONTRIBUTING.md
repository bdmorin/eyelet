# Contributing to Rigging

🎉 First off, thanks for taking the time to contribute! 🎉

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps to reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include your OS, Python version, and Rigging version

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/rigging
cd rigging

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install in development mode
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

## Running Tests

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=rigging

# Run linting
uv run ruff check .

# Format code
uv run black .
```

## Code Style

* We use [Black](https://github.com/psf/black) for code formatting
* We use [Ruff](https://github.com/astral-sh/ruff) for linting
* Follow PEP 8
* Use type hints where possible
* Write docstrings for all public functions

## Naval Tradition

When adding new features or commands, try to maintain the naval theme:
- Use nautical terminology where appropriate
- Keep the playful spirit of "All hands to the rigging!"
- But don't let it get in the way of clarity

## License

By contributing, you agree that your contributions will be licensed under the MIT License.