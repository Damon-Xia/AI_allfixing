# Contributing to AI AllFixing

Thank you for your interest in contributing to AI AllFixing! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- An API key for at least one supported AI provider (OpenAI, Anthropic, etc.)

### Development Setup

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/AI_allfixing.git
cd AI_allfixing
```

2. **Create a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install in development mode:**

```bash
pip install -e ".[dev]"
```

4. **Install pre-commit hooks:**

```bash
pre-commit install
```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Making Changes

1. Create a new branch from `main`
2. Make your changes
3. Write or update tests as needed
4. Run the test suite: `pytest`
5. Run linting: `ruff check .`
6. Run type checking: `mypy src/`
7. Commit with a clear message

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`

**Examples:**
- `feat(tools): add image analysis tool`
- `fix(code-fixer): handle syntax errors in Python 3.12`
- `docs: update installation guide`

### Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update the CHANGELOG if applicable
4. Request review from maintainers
5. Address review feedback

## Adding a New Tool

AI AllFixing is designed to be easily extensible. To add a new tool:

1. Create a new module in `src/ai_allfixing/tools/`
2. Inherit from `BaseTool` class
3. Implement required methods: `execute()`, `validate_input()`
4. Add CLI commands in `src/ai_allfixing/cli/`
5. Write tests in `tests/tools/`
6. Add documentation in `docs/`

See [Adding Custom Tools](docs/custom-tools.md) for detailed instructions.

## Code Style

- We use **Ruff** for linting and formatting
- Maximum line length: 100 characters
- Use type hints for all function signatures
- Write docstrings for all public functions and classes (Google style)

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_allfixing --cov-report=html

# Run specific test file
pytest tests/tools/test_code_fixer.py

# Run tests matching a pattern
pytest -k "test_fix"
```

## Reporting Issues

- Use the GitHub issue templates
- Include reproduction steps
- Include Python version and OS information
- Include relevant error messages and logs

## Questions?

Feel free to open a [Discussion](https://github.com/Damon-Xia/AI_allfixing/discussions) for questions or ideas.

---

Thank you for helping make AI AllFixing better!
