"""Text Summarizer - Summarize long documents into concise key points."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus


SYSTEM_PROMPT = """You are an expert text summarizer. Your job is to:
1. Read the provided text carefully.
2. Extract the key points and main ideas.
3. Produce a clear, concise summary.

Rules:
- Maintain accuracy - don't add information not in the original.
- Preserve the tone and intent of the original text.
- Use bullet points for multiple key points.
- Respect the requested length/format constraints.
"""


class TextSummarizer(BaseTool):
    """AI-powered text summarizer for documents, articles, and long text.

    Supports multiple output formats and length constraints.

    Example:
        ```python
        summarizer = TextSummarizer()
        result = await summarizer.run(long_article, max_length=200)
        print(result.output)
        ```
    """

    name = "text_summarizer"
    description = "Summarize long documents, articles, and text into concise key points"
    version = "0.1.0"

    def validate_input(self, input_data: Any) -> None:
        """Validate that input is non-empty text.

        Args:
            input_data: Text to validate.

        Raises:
            ValueError: If input is empty or not a string.
        """
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string of text")
        if not input_data.strip():
            raise ValueError("Input text cannot be empty")

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Summarize the provided text.

        Args:
            input_data: The text to summarize.
            **kwargs: Additional options:
                - max_length: Maximum word count for summary.
                - format: Output format (bullets, paragraph, one_line).
                - language: Output language (default: same as input).

        Returns:
            ToolResult with summary.
        """
        max_length = kwargs.get("max_length", 200)
        output_format = kwargs.get("format", "bullets")
        language = kwargs.get("language", "")

        user_prompt = f"Summarize the following text"
        if max_length:
            user_prompt += f" (max {max_length} words)"

        format_instructions = {
            "bullets": "Use bullet points for key takeaways.",
            "paragraph": "Write as a concise paragraph.",
            "one_line": "Summarize in a single sentence.",
        }
        user_prompt += f".\n\nFormat: {format_instructions.get(output_format, output_format)}"

        if language:
            user_prompt += f"\nOutput language: {language}"

        user_prompt += f"\n\nText:\n{input_data}"

        response = await self.provider.complete_with_system(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=response.content,
            metadata={
                "format": output_format,
                "model": response.model,
                "input_length": len(input_data.split()),
            },
            tokens_used=response.total_tokens,
        )
