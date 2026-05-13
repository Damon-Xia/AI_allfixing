"""Core engine for managing providers and tool execution."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.base import BaseTool, ToolResult
from ai_allfixing.core.config import Config
from ai_allfixing.providers.base import BaseProvider
from ai_allfixing.utils.logger import get_logger

logger = get_logger(__name__)


class Engine:
    """Central engine that manages providers and executes tools.

    The Engine is responsible for:
    - Initializing and managing LLM providers
    - Providing a unified interface for tool execution
    - Handling provider fallback and retry logic

    Example:
        ```python
        from ai_allfixing.core import Engine, Config

        config = Config()
        engine = Engine(config=config)
        provider = engine.get_provider()
        response = await provider.complete("Fix this code: ...")
        ```
    """

    def __init__(self, config: Config | None = None) -> None:
        """Initialize the engine.

        Args:
            config: Configuration object. Uses default if None.
        """
        self.config = config or Config()
        self._providers: dict[str, BaseProvider] = {}

    def get_provider(self, name: str | None = None) -> BaseProvider:
        """Get or create a provider instance.

        Args:
            name: Provider name. Uses config default if None.

        Returns:
            BaseProvider instance.

        Raises:
            ValueError: If provider name is unknown.
        """
        provider_name = name or self.config.provider.name

        if provider_name in self._providers:
            return self._providers[provider_name]

        provider = self._create_provider(provider_name)
        self._providers[provider_name] = provider
        return provider

    def _create_provider(self, name: str) -> BaseProvider:
        """Create a new provider instance.

        Args:
            name: Provider name.

        Returns:
            BaseProvider instance.

        Raises:
            ValueError: If provider name is unknown.
        """
        if name == "openai":
            from ai_allfixing.providers.openai_provider import OpenAIProvider

            return OpenAIProvider(config=self.config.provider)
        elif name == "anthropic":
            from ai_allfixing.providers.anthropic_provider import AnthropicProvider

            return AnthropicProvider(config=self.config.provider)
        else:
            raise ValueError(
                f"Unknown provider: {name!r}. "
                f"Supported providers: openai, anthropic"
            )

    async def run_tool(self, tool: BaseTool, input_data: Any, **kwargs: Any) -> ToolResult:
        """Execute a tool with the engine's provider.

        Args:
            tool: The tool instance to execute.
            input_data: Input data for the tool.
            **kwargs: Additional arguments for the tool.

        Returns:
            ToolResult with the execution outcome.
        """
        logger.info(f"Running tool: {tool.name}")
        result = await tool.run(input_data, **kwargs)
        logger.info(
            f"Tool {tool.name} completed with status: {result.status.value} "
            f"(tokens: {result.tokens_used})"
        )
        return result

    def list_providers(self) -> list[str]:
        """List available provider names.

        Returns:
            List of supported provider names.
        """
        return ["openai", "anthropic"]
