"""Code Fixer - Automatically detect and fix bugs, syntax errors, and code smells."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus


SYSTEM_PROMPT = """You are an expert code fixer. Your job is to:
1. Analyze the provided code for bugs, syntax errors, and code smells.
2. Fix all issues while maintaining the original intent.
3. Return ONLY the fixed code without explanations.
4. If the code is already correct, return it unchanged.

Rules:
- Preserve the original coding style and formatting as much as possible.
- Fix logical errors, type errors, and common pitfalls.
- Do not add new features or refactor unless necessary to fix a bug.
- If the language is ambiguous, assume Python unless context suggests otherwise.
"""


class CodeFixer(BaseTool):
    """AI-powered code fixer that detects and repairs bugs automatically.

    Analyzes code for syntax errors, logical bugs, type issues,
    and common anti-patterns, then returns the corrected version.

    Example:
        ```python
        fixer = CodeFixer()
        result = await fixer.run("def add(a, b)\\n  return a + b")
        print(result.output)  # Fixed code with proper syntax
        ```
    """

    name = "code_fixer"
    description = "Automatically detect and fix bugs, syntax errors, and code smells"
    version = "0.1.0"

    def validate_input(self, input_data: Any) -> None:
        """Validate that input is non-empty code string.

        Args:
            input_data: Code string to validate.

        Raises:
            ValueError: If input is empty or not a string.
        """
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string of code")
        if not input_data.strip():
            raise ValueError("Input code cannot be empty")

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Fix the provided code.

        Args:
            input_data: The code to fix.
            **kwargs: Additional options:
                - language: Programming language hint.
                - explain: If True, include explanation in metadata.

        Returns:
            ToolResult with fixed code.
        """
        language = kwargs.get("language", "")
        explain = kwargs.get("explain", False)

        user_prompt = f"Fix the following code"
        if language:
            user_prompt += f" ({language})"
        user_prompt += f":\n\n```\n{input_data}\n```"

        if explain:
            user_prompt += "\n\nAlso briefly explain what was fixed."

        response = await self.provider.complete_with_system(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=response.content,
            metadata={
                "language": language,
                "model": response.model,
            },
            tokens_used=response.total_tokens,
        )
