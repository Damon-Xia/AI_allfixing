"""Base classes for all AI tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ToolStatus(Enum):
    """Status of a tool execution."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


@dataclass
class ToolResult:
    """Result of a tool execution.

    Attributes:
        status: The execution status.
        output: The main output content.
        metadata: Additional metadata about the execution.
        error: Error message if status is ERROR.
        tokens_used: Number of tokens consumed.
    """

    status: ToolStatus
    output: str
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    tokens_used: int = 0

    @property
    def success(self) -> bool:
        """Check if the execution was successful."""
        return self.status == ToolStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "status": self.status.value,
            "output": self.output,
            "metadata": self.metadata,
            "error": self.error,
            "tokens_used": self.tokens_used,
        }


class BaseTool(ABC):
    """Abstract base class for all AI-powered tools.

    All tools must inherit from this class and implement the
    `execute` and `validate_input` methods.

    Example:
        ```python
        class MyTool(BaseTool):
            name = "my_tool"
            description = "Does something useful"

            def validate_input(self, input_data):
                if not input_data:
                    raise ValueError("Input cannot be empty")

            async def execute(self, input_data, **kwargs):
                result = await self._call_llm(prompt)
                return ToolResult(status=ToolStatus.SUCCESS, output=result)
        ```
    """

    name: str = "base_tool"
    description: str = "Base tool"
    version: str = "0.1.0"

    def __init__(self, config: Any | None = None, provider: Any | None = None) -> None:
        """Initialize the tool.

        Args:
            config: Configuration object. If None, uses default config.
            provider: LLM provider instance. If None, uses default provider.
        """
        from ai_allfixing.core.config import Config

        self.config = config or Config()
        self._provider = provider

    @property
    def provider(self) -> Any:
        """Get the LLM provider, initializing if needed."""
        if self._provider is None:
            from ai_allfixing.core.engine import Engine

            engine = Engine(config=self.config)
            self._provider = engine.get_provider()
        return self._provider

    @abstractmethod
    def validate_input(self, input_data: Any) -> None:
        """Validate input data before execution.

        Args:
            input_data: The input to validate.

        Raises:
            ValueError: If input is invalid.
        """
        ...

    @abstractmethod
    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Execute the tool with given input.

        Args:
            input_data: The main input data.
            **kwargs: Additional keyword arguments.

        Returns:
            ToolResult with the execution outcome.
        """
        ...

    async def run(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Validate and execute the tool.

        This is the main entry point that handles validation
        and error handling around execution.

        Args:
            input_data: The main input data.
            **kwargs: Additional keyword arguments.

        Returns:
            ToolResult with the execution outcome.
        """
        try:
            self.validate_input(input_data)
            return await self.execute(input_data, **kwargs)
        except ValueError as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Validation error: {e}",
            )
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Execution error: {e}",
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name!r}, version={self.version!r})>"
