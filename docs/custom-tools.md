# Adding Custom Tools

AI AllFixing is designed to be easily extensible. You can create your own AI-powered tools by inheriting from the `BaseTool` class.

## Basic Structure

```python
from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus
from typing import Any


class MyCustomTool(BaseTool):
    """Description of what your tool does."""

    name = "my_tool"
    description = "Brief description"
    version = "0.1.0"

    def validate_input(self, input_data: Any) -> None:
        """Validate input before execution."""
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string")
        if not input_data.strip():
            raise ValueError("Input cannot be empty")

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Execute the tool logic."""
        # Define your system prompt
        system_prompt = "You are an expert at..."

        # Build the user prompt
        user_prompt = f"Process this: {input_data}"

        # Call the LLM
        response = await self.provider.complete_with_system(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Return the result
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=response.content,
            metadata={"model": response.model},
            tokens_used=response.total_tokens,
        )
```

## Step-by-Step Guide

### 1. Create Your Tool Module

Create a new file at `src/ai_allfixing/tools/my_tool.py`.

### 2. Define the System Prompt

The system prompt sets the AI's behavior. Be specific and clear:

```python
SYSTEM_PROMPT = """You are an expert at [specific task].
Your job is to:
1. [First responsibility]
2. [Second responsibility]
3. [Third responsibility]

Rules:
- [Important constraint]
- [Another constraint]
- [Output format instruction]
"""
```

### 3. Implement validate_input

Validate early to fail fast with clear error messages:

```python
def validate_input(self, input_data: Any) -> None:
    if not isinstance(input_data, str):
        raise ValueError("Input must be a string")
    if len(input_data) > 100000:
        raise ValueError("Input too long (max 100k chars)")
    if not input_data.strip():
        raise ValueError("Input cannot be empty")
```

### 4. Implement execute

The main logic. Always return a `ToolResult`:

```python
async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
    # Extract options
    option_a = kwargs.get("option_a", "default")

    # Build prompt
    user_prompt = f"Process with {option_a}: {input_data}"

    # Call LLM
    response = await self.provider.complete_with_system(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    # Return result
    return ToolResult(
        status=ToolStatus.SUCCESS,
        output=response.content,
        metadata={"option_a": option_a, "model": response.model},
        tokens_used=response.total_tokens,
    )
```

### 5. Register in __init__.py

Add your tool to `src/ai_allfixing/tools/__init__.py`:

```python
from ai_allfixing.tools.my_tool import MyCustomTool

__all__ = [..., "MyCustomTool"]
```

### 6. Add CLI Commands (Optional)

Add commands to `src/ai_allfixing/cli/main.py`:

```python
@cli.command("my-command")
@click.argument("input_text")
@click.pass_context
def my_command(ctx, input_text):
    """Description of the command."""
    import asyncio
    from ai_allfixing.tools.my_tool import MyCustomTool
    from ai_allfixing.cli._helpers import get_config

    config = get_config(ctx)
    tool = MyCustomTool(config=config)
    result = asyncio.run(tool.run(input_text))

    if result.success:
        console.print(result.output)
    else:
        console.print(f"[red]Error:[/red] {result.error}")
```

### 7. Write Tests

```python
# tests/test_tools/test_my_tool.py
import pytest
from unittest.mock import MagicMock
from ai_allfixing.tools.my_tool import MyCustomTool


class TestMyCustomTool:
    def test_validate_input_valid(self):
        tool = MyCustomTool(provider=MagicMock())
        tool.validate_input("valid input")

    def test_validate_input_empty(self):
        tool = MyCustomTool(provider=MagicMock())
        with pytest.raises(ValueError):
            tool.validate_input("")

    @pytest.mark.asyncio
    async def test_execute(self, mock_provider):
        tool = MyCustomTool(provider=mock_provider)
        result = await tool.run("test input")
        assert result.success
```

## Best Practices

1. **Keep system prompts focused** - One clear task per tool
2. **Validate early** - Catch errors before making API calls
3. **Include metadata** - Help users understand what happened
4. **Handle edge cases** - Empty input, very long input, etc.
5. **Write tests** - Both unit tests and integration tests
6. **Document thoroughly** - Include usage examples
