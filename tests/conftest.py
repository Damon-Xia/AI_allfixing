"""Shared test fixtures and configuration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_allfixing.core.config import Config, ProviderConfig
from ai_allfixing.providers.base import CompletionResponse


@pytest.fixture
def mock_config() -> Config:
    """Create a test configuration."""
    return Config(
        provider=ProviderConfig(
            name="openai",
            api_key="test-key-12345",
            model="gpt-4o",
            max_tokens=1000,
            temperature=0.0,
        ),
        log_level="DEBUG",
        cache_enabled=False,
    )


@pytest.fixture
def mock_provider() -> MagicMock:
    """Create a mock LLM provider."""
    provider = MagicMock()
    provider.complete = AsyncMock(
        return_value=CompletionResponse(
            content="Mock response",
            model="gpt-4o",
            tokens_input=10,
            tokens_output=20,
            finish_reason="stop",
        )
    )
    provider.complete_chat = AsyncMock(
        return_value=CompletionResponse(
            content="Mock chat response",
            model="gpt-4o",
            tokens_input=15,
            tokens_output=25,
            finish_reason="stop",
        )
    )
    provider.complete_with_system = AsyncMock(
        return_value=CompletionResponse(
            content="Mock system response",
            model="gpt-4o",
            tokens_input=20,
            tokens_output=30,
            finish_reason="stop",
        )
    )
    return provider


@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code with bugs for testing."""
    return '''def calculate_average(numbers):
    total = 0
    for num in numbers
        total += num
    return total / len(numbers)

def greet(name)
    print(f"Hello, {name}!")
    return
'''


@pytest.fixture
def sample_clean_code() -> str:
    """Sample clean Python code for testing."""
    return '''def calculate_average(numbers: list[float]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
'''
