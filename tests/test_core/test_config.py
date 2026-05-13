"""Tests for configuration management."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ai_allfixing.core.config import Config, ProviderConfig


class TestProviderConfig:
    """Tests for ProviderConfig."""

    def test_default_values(self) -> None:
        config = ProviderConfig()
        assert config.name == "openai"
        assert config.model == "gpt-4o"
        assert config.max_tokens == 4096
        assert config.temperature == 0.1
        assert config.api_key == ""
        assert config.base_url is None

    def test_custom_values(self) -> None:
        config = ProviderConfig(
            name="anthropic",
            api_key="sk-test",
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
        )
        assert config.name == "anthropic"
        assert config.api_key == "sk-test"
        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tokens == 8192


class TestConfig:
    """Tests for Config."""

    def test_default_config(self) -> None:
        config = Config()
        assert config.provider.name == "openai"
        assert config.log_level == "INFO"
        assert config.cache_enabled is True
        assert config.output_format == "text"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-test-key"})
    def test_load_api_key_from_env(self) -> None:
        config = Config()
        assert config.provider.api_key == "env-test-key"

    def test_set_and_get(self) -> None:
        config = Config()
        config.set("provider.model", "gpt-4")
        assert config.get("provider.model") == "gpt-4"

    def test_set_invalid_key(self) -> None:
        config = Config()
        with pytest.raises(KeyError):
            config.set("invalid.nested.key", "value")

    def test_save_and_load(self, tmp_path: Path) -> None:
        config = Config(
            provider=ProviderConfig(name="anthropic", model="claude-3-opus"),
            log_level="DEBUG",
        )
        config_file = tmp_path / "config.yaml"
        config.save(config_file)

        loaded = Config.from_file(config_file)
        assert loaded.provider.name == "anthropic"
        assert loaded.provider.model == "claude-3-opus"
        assert loaded.log_level == "DEBUG"

    def test_from_file_missing(self, tmp_path: Path) -> None:
        """Loading from non-existent file returns defaults."""
        config = Config.from_file(tmp_path / "nonexistent.yaml")
        assert config.provider.name == "openai"
