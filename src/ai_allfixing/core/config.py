"""Configuration management for AI AllFixing."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_DIR = Path.home() / ".ai-allfixing"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider.

    Attributes:
        name: Provider name (openai, anthropic, local).
        api_key: API key for the provider.
        model: Default model to use.
        base_url: Custom API base URL (for local/Azure).
        max_tokens: Maximum tokens for responses.
        temperature: Sampling temperature.
        extra: Additional provider-specific settings.
    """

    name: str = "openai"
    api_key: str = ""
    model: str = "gpt-4o"
    base_url: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.1
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Config:
    """Main configuration for AI AllFixing.

    Attributes:
        provider: Active provider configuration.
        log_level: Logging level.
        cache_enabled: Whether to cache LLM responses.
        cache_dir: Directory for cached responses.
        output_format: Default output format (text, json, markdown).
    """

    provider: ProviderConfig = field(default_factory=ProviderConfig)
    log_level: str = "INFO"
    cache_enabled: bool = True
    cache_dir: Path = field(default_factory=lambda: DEFAULT_CONFIG_DIR / "cache")
    output_format: str = "text"

    def __post_init__(self) -> None:
        """Load API keys from environment variables if not set."""
        if not self.provider.api_key:
            self._load_api_key_from_env()

    def _load_api_key_from_env(self) -> None:
        """Try to load API key from environment variables."""
        env_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "azure": "AZURE_OPENAI_API_KEY",
        }
        env_var = env_mapping.get(self.provider.name, "")
        if env_var:
            self.provider.api_key = os.environ.get(env_var, "")

    @classmethod
    def from_file(cls, path: Path | str | None = None) -> "Config":
        """Load configuration from a YAML file.

        Args:
            path: Path to config file. Uses default if None.

        Returns:
            Config instance.
        """
        config_path = Path(path) if path else DEFAULT_CONFIG_FILE

        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        provider_data = data.get("provider", {})
        provider = ProviderConfig(
            name=provider_data.get("name", "openai"),
            api_key=provider_data.get("api_key", ""),
            model=provider_data.get("model", "gpt-4o"),
            base_url=provider_data.get("base_url"),
            max_tokens=provider_data.get("max_tokens", 4096),
            temperature=provider_data.get("temperature", 0.1),
            extra=provider_data.get("extra", {}),
        )

        return cls(
            provider=provider,
            log_level=data.get("log_level", "INFO"),
            cache_enabled=data.get("cache_enabled", True),
            cache_dir=Path(data.get("cache_dir", str(DEFAULT_CONFIG_DIR / "cache"))),
            output_format=data.get("output_format", "text"),
        )

    def save(self, path: Path | str | None = None) -> None:
        """Save configuration to a YAML file.

        Args:
            path: Path to save to. Uses default if None.
        """
        config_path = Path(path) if path else DEFAULT_CONFIG_FILE
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "provider": {
                "name": self.provider.name,
                "api_key": self.provider.api_key,
                "model": self.provider.model,
                "base_url": self.provider.base_url,
                "max_tokens": self.provider.max_tokens,
                "temperature": self.provider.temperature,
                "extra": self.provider.extra,
            },
            "log_level": self.log_level,
            "cache_enabled": self.cache_enabled,
            "cache_dir": str(self.cache_dir),
            "output_format": self.output_format,
        }

        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by dot-notation key.

        Args:
            key: Dot-separated key (e.g., 'provider.model').
            value: Value to set.
        """
        parts = key.split(".")
        if len(parts) == 2 and parts[0] == "provider":
            setattr(self.provider, parts[1], value)
        elif len(parts) == 1:
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"Unknown config key: {key}")
        else:
            raise KeyError(f"Unknown config key: {key}")

    def get(self, key: str) -> Any:
        """Get a configuration value by dot-notation key.

        Args:
            key: Dot-separated key (e.g., 'provider.model').

        Returns:
            The configuration value.
        """
        parts = key.split(".")
        if len(parts) == 2 and parts[0] == "provider":
            return getattr(self.provider, parts[1])
        elif len(parts) == 1:
            return getattr(self, key)
        else:
            raise KeyError(f"Unknown config key: {key}")
