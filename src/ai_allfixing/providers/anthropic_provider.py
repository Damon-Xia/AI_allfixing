"""Anthropic (Claude) provider implementation."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.config import ProviderConfig
from ai_allfixing.providers.base import BaseProvider, CompletionResponse, Message


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude models.

    Supports Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku, etc.

    Example:
        ```python
        from ai_allfixing.providers import AnthropicProvider
        from ai_allfixing.core.config import ProviderConfig

        config = ProviderConfig(
            name="anthropic",
            api_key="sk-ant-...",
            model="claude-sonnet-4-20250514",
        )
        provider = AnthropicProvider(config=config)
        response = await provider.complete("Hello!")
        print(response.content)
        ```
    """

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize Anthropic provider.

        Args:
            config: Provider configuration with API key and model.
        """
        super().__init__(config)

    @property
    def client(self) -> Any:
        """Lazy-initialize the Anthropic async client."""
        if self._client is None:
            from anthropic import AsyncAnthropic

            kwargs: dict[str, Any] = {"api_key": self.config.api_key}
            if self.config.base_url:
                kwargs["base_url"] = self.config.base_url

            self._client = AsyncAnthropic(**kwargs)
        return self._client

    async def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Generate a completion from a text prompt.

        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters.

        Returns:
            CompletionResponse with the result.
        """
        messages = [Message(role="user", content=prompt)]
        return await self.complete_chat(messages, **kwargs)

    async def complete_chat(
        self, messages: list[Message], **kwargs: Any
    ) -> CompletionResponse:
        """Generate a chat completion using Anthropic's API.

        Args:
            messages: List of Message objects.
            **kwargs: Additional parameters.

        Returns:
            CompletionResponse with the result.
        """
        model = kwargs.pop("model", self.config.model)
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens)

        # Anthropic uses a separate system parameter
        system_prompt = ""
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        # Ensure at least one user message
        if not chat_messages:
            chat_messages = [{"role": "user", "content": ""}]

        api_kwargs: dict[str, Any] = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            api_kwargs["system"] = system_prompt

        api_kwargs.update(kwargs)

        response = await self.client.messages.create(**api_kwargs)

        # Extract text content
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        return CompletionResponse(
            content=content,
            model=response.model,
            tokens_input=response.usage.input_tokens,
            tokens_output=response.usage.output_tokens,
            finish_reason=response.stop_reason or "end_turn",
            raw=response,
        )
