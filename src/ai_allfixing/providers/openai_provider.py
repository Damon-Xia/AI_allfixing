"""OpenAI provider implementation."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.config import ProviderConfig
from ai_allfixing.providers.base import BaseProvider, CompletionResponse, Message


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI and OpenAI-compatible APIs.

    Supports GPT-4o, GPT-4, GPT-3.5, and any OpenAI-compatible endpoint
    (Azure OpenAI, local vLLM, etc.).

    Example:
        ```python
        from ai_allfixing.providers import OpenAIProvider
        from ai_allfixing.core.config import ProviderConfig

        config = ProviderConfig(
            name="openai",
            api_key="sk-...",
            model="gpt-4o",
        )
        provider = OpenAIProvider(config=config)
        response = await provider.complete("Hello!")
        print(response.content)
        ```
    """

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize OpenAI provider.

        Args:
            config: Provider configuration with API key and model.
        """
        super().__init__(config)

    @property
    def client(self) -> Any:
        """Lazy-initialize the OpenAI async client."""
        if self._client is None:
            from openai import AsyncOpenAI

            kwargs: dict[str, Any] = {"api_key": self.config.api_key}
            if self.config.base_url:
                kwargs["base_url"] = self.config.base_url

            self._client = AsyncOpenAI(**kwargs)
        return self._client

    async def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Generate a completion from a text prompt.

        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters (model, temperature, max_tokens, etc.).

        Returns:
            CompletionResponse with the result.
        """
        messages = [Message(role="user", content=prompt)]
        return await self.complete_chat(messages, **kwargs)

    async def complete_chat(
        self, messages: list[Message], **kwargs: Any
    ) -> CompletionResponse:
        """Generate a chat completion.

        Args:
            messages: List of Message objects.
            **kwargs: Additional parameters.

        Returns:
            CompletionResponse with the result.
        """
        model = kwargs.pop("model", self.config.model)
        temperature = kwargs.pop("temperature", self.config.temperature)
        max_tokens = kwargs.pop("max_tokens", self.config.max_tokens)

        formatted_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        choice = response.choices[0]
        usage = response.usage

        return CompletionResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_input=usage.prompt_tokens if usage else 0,
            tokens_output=usage.completion_tokens if usage else 0,
            finish_reason=choice.finish_reason or "stop",
            raw=response,
        )
