.PHONY: help install dev lint format test test-cov build clean docs

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

dev:  ## Install with dev dependencies
	pip install -e ".[dev]"
	pre-commit install

lint:  ## Run linters
	ruff check .
	mypy src/ --ignore-missing-imports

format:  ## Format code
	ruff format .
	ruff check --fix .

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=ai_allfixing --cov-report=html --cov-report=term-missing

build:  ## Build package
	python -m build

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docs:  ## Build documentation
	mkdocs build

docs-serve:  ## Serve documentation locally
	mkdocs serve

publish:  ## Publish to PyPI (requires credentials)
	python -m build
	twine upload dist/*
