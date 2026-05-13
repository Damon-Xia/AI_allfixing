"""Doc Generator - Auto-generate documentation from source code."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus


SYSTEM_PROMPT = """You are an expert documentation generator. Your job is to:
1. Analyze the provided source code.
2. Generate clear, comprehensive documentation.
3. Include function signatures, parameter descriptions, return values, and examples.

Rules:
- Follow the specified documentation style (Google, NumPy, Sphinx).
- Include type information when available.
- Write concise but informative descriptions.
- Add usage examples where helpful.
- Document edge cases and exceptions.
"""


class DocGenerator(BaseTool):
    """AI-powered documentation generator from source code.

    Generates docstrings, API docs, and README content from code.

    Example:
        ```python
        doc_gen = DocGenerator()
        result = await doc_gen.run(source_code, style="google")
        print(result.output)  # Generated documentation
        ```
    """

    name = "doc_generator"
    description = "Auto-generate documentation from source code"
    version = "0.1.0"

    def validate_input(self, input_data: Any) -> None:
        """Validate that input is non-empty code string.

        Args:
            input_data: Code to validate.

        Raises:
            ValueError: If input is empty or not a string.
        """
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string of source code")
        if not input_data.strip():
            raise ValueError("Input source code cannot be empty")

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        """Generate documentation for the provided code.

        Args:
            input_data: The source code to document.
            **kwargs: Additional options:
                - style: Doc style (google, numpy, sphinx). Default: google.
                - output_type: Type of docs (docstring, readme, api). Default: docstring.
                - language: Programming language hint.

        Returns:
            ToolResult with generated documentation.
        """
        style = kwargs.get("style", "google")
        output_type = kwargs.get("output_type", "docstring")
        language = kwargs.get("language", "")

        user_prompt = f"Generate {output_type} documentation"
        if language:
            user_prompt += f" for this {language} code"
        user_prompt += f" using {style} style.\n\n```\n{input_data}\n```"

        response = await self.provider.complete_with_system(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=response.content,
            metadata={
                "style": style,
                "output_type": output_type,
                "model": response.model,
            },
            tokens_used=response.total_tokens,
        )
