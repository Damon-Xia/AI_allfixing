"""Shell Assistant - Natural language to shell commands conversion."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus


SYSTEM_PROMPT = """You are an expert shell/terminal assistant. Your job is to:
1. Convert natural language descriptions into shell commands.
2. Provide safe, correct commands for the target OS/shell.
3. Explain what each command does.

Rules:
- Default to bash on Linux/macOS unless specified.
- NEVER suggest destructive commands without explicit warning.
- Prefer safe operations (e.g., use 'rm -i' instead of 'rm -rf').
- Provide the command first, then a brief explanation.
- For complex tasks, break into numbered steps.

Output format:
```bash
command here
```
Explanation: Brief description of what the command does.
"""


class ShellAssistant(BaseTool):
    """AI-powered shell assistant that converts natural language to commands.

    Translates natural language descriptions into correct shell commands
    with safety checks and explanations.

    Example:
        ```python
        shell = ShellAssistant()
        result = await shell.run("find all python files modified in the last 7 days")
        print(result.output)
        # ```bash
        # find . -name "*.py" -mtime -7
        # ```
        # Explanation: Finds all .py files modified within the last 7 days.
        ```
    """

    name = "shell_assistant"
    description = "Natural language to shell commands conversion"
    version = "0.1.0"

    def validate_input(self, input_data: Any) -> None:
        """Validate that input is a non-empty natural language description.

        Args:
            input_data: Description to validate.

        Raises:
            ValueError: If input is empty or not a string.
        """
        if not isinstance(input_data, str):
            raise ValueError("Input must be a natural language description")
        if not input_data.strip():
            raise ValueError("Input description cannot be empty")

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Convert natural language to shell command.

        Args:
            input_data: Natural language description of desired action.
            **kwargs: Additional options:
                - os: Target OS (linux, macos, windows). Default: linux.
                - shell: Target shell (bash, zsh, fish, powershell). Default: bash.
                - safe_mode: If True, prefer safe alternatives. Default: True.

        Returns:
            ToolResult with shell command and explanation.
        """
        target_os = kwargs.get("os", "linux")
        shell = kwargs.get("shell", "bash")
        safe_mode = kwargs.get("safe_mode", True)

        user_prompt = f"Convert this to a {shell} command (OS: {target_os}):\n\n{input_data}"

        if safe_mode:
            user_prompt += "\n\nPrefer safe alternatives (confirm before destructive ops)."

        response = await self.provider.complete_with_system(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=response.content,
            metadata={
                "os": target_os,
                "shell": shell,
                "safe_mode": safe_mode,
                "model": response.model,
            },
            tokens_used=response.total_tokens,
        )
