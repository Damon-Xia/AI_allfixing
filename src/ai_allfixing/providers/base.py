"""Base provider interface for LLM integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ai_allfixing.core.config import ProviderConfig


@dataclass
class Message:
    """A chat message.

    Attributes:
        role: The role (system, user, assistant).
        content: The message content.
    """

    role: str
    content: str


@dataclass
class CompletionResponse:
    """Response from an LLM completion.

    Attributes:
        content: The response text.
        model: The model used.
        tokens_input: Number of input tokens.
        tokens_output: Number of output tokens.
        finish_reason: Why the completion stopped.
        raw: The raw response object from the provider.
    """

    content: str
    model: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    finish_reason: str = "stop"
    raw: Any = None

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.tokens_input + self.tokens_output


class BaseProvider(ABC):
    """Abstract base class for LLM providers.

    All provider implementations must inherit from this class
    and implement the `complete` and `complete_chat` methods.

    Example:
        ```python
        class MyProvider(BaseProvider):
            async def complete(self, prompt, **kwargs):
                # Call the LLM API
                ...

            async def complete_chat(self, messages, **kwargs):
                # Call the chat API
                ...
        ```
    """

    def __init__(self, config: ProviderConfig) -> None:
        """Initialize the provider.

        Args:
            config: Provider configuration.
        """
        self.config = config
        self._client: Any = None

    @property
    def model(self) -> str:
        """Get the configured model name."""
        return self.config.model

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Generate a completion from a text prompt.

        Args:
            prompt: The input prompt.
            **kwargs: Additional provider-specific parameters.

        Returns:
            CompletionResponse with the result.
        """
        ...

    @abstractmethod
    async def complete_chat(
        self, messages: list[Message], **kwargs: Any
    ) -> CompletionResponse:
        """Generate a completion from chat messages.

        Args:
            messages: List of Message objects.
            **kwargs: Additional provider-specific parameters.

        Returns:
            CompletionResponse with the result.
        """
        ...

    async def complete_with_system(
        self, system_prompt: str, user_prompt: str, **kwargs: Any
    ) -> CompletionResponse:
        """Convenience method: complete with system + user message.

        Args:
            system_prompt: The system instruction.
            user_prompt: The user input.
            **kwargs: Additional parameters.

        Returns:
            CompletionResponse with the result.
        """
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_prompt),
        ]
        return await self.complete_chat(messages, **kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(model={self.model!r})>"
