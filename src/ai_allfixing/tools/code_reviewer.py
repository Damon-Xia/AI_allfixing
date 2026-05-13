"""Code Reviewer - Get instant AI code reviews with actionable suggestions."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus


SYSTEM_PROMPT = """You are an expert code reviewer. Your job is to:
1. Analyze the code for quality, correctness, and best practices.
2. Identify potential bugs, security issues, and performance problems.
3. Provide actionable, constructive feedback.

Structure your review as:
## Summary
Brief overall assessment.

## Issues Found
- [SEVERITY] Description of issue (line reference if applicable)

## Suggestions
- Specific improvement suggestions with code examples.

## Good Practices
- Things done well (positive reinforcement).

Severity levels: CRITICAL, WARNING, INFO
"""


class CodeReviewer(BaseTool):
    """AI-powered code reviewer providing instant actionable feedback.

    Analyzes code for quality, security, performance, and best practices.

    Example:
        ```python
        reviewer = CodeReviewer()
        result = await reviewer.run(code, language="python")
        print(result.output)  # Detailed review with suggestions
        ```
    """

    name = "code_reviewer"
    description = "Get instant AI code reviews with actionable suggestions"
    version = "0.1.0"

    def validate_input(self, input_data: Any) -> None:
        """Validate that input is non-empty code string.

        Args:
            input_data: Code to validate.

        Raises:
            ValueError: If input is empty or not a string.
        """
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string of code")
        if not input_data.strip():
            raise ValueError("Input code cannot be empty")

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Review the provided code.

        Args:
            input_data: The code to review.
            **kwargs: Additional options:
                - language: Programming language.
                - focus: Review focus (security, performance, style, all).
                - context: Additional context about the code.

        Returns:
            ToolResult with review feedback.
        """
        language = kwargs.get("language", "")
        focus = kwargs.get("focus", "all")
        context = kwargs.get("context", "")

        user_prompt = f"Review the following code"
        if language:
            user_prompt += f" ({language})"
        user_prompt += "."

        if focus != "all":
            user_prompt += f"\nFocus area: {focus}"
        if context:
            user_prompt += f"\nContext: {context}"

        user_prompt += f"\n\n```\n{input_data}\n```"

        response = await self.provider.complete_with_system(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=response.content,
            metadata={
                "language": language,
                "focus": focus,
                "model": response.model,
            },
            tokens_used=response.total_tokens,
        )
