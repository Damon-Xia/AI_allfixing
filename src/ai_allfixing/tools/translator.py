"""Translator - AI-powered translation supporting 50+ languages."""

from __future__ import annotations

from typing import Any

from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus


SYSTEM_PROMPT = """You are an expert multilingual translator. Your job is to:
1. Detect the source language (or use the specified one).
2. Translate the text to the target language naturally and accurately.
3. Preserve formatting, tone, and cultural nuances.

Rules:
- Produce natural, fluent translations (not word-for-word).
- Preserve technical terms and proper nouns appropriately.
- Maintain the original formatting (paragraphs, lists, etc.).
- Return ONLY the translation without explanations.
"""

LANGUAGE_MAP = {
    "zh": "Chinese (Simplified)",
    "en": "English",
    "ja": "Japanese",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "it": "Italian",
    "nl": "Dutch",
    "th": "Thai",
    "vi": "Vietnamese",
    "hi": "Hindi",
}


class Translator(BaseTool):
    """AI-powered translator supporting 50+ languages with context awareness.

    Provides natural, fluent translations preserving tone and nuance.

    Example:
        ```python
        translator = Translator()
        result = await translator.run("Hello, World!", target_lang="zh")
        print(result.output)  # "你好，世界！"
        ```
    """

    name = "translator"
    description = "AI-powered translation supporting 50+ languages with context awareness"
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
        """Translate the provided text.

        Args:
            input_data: The text to translate.
            **kwargs: Additional options:
                - target_lang: Target language code (e.g., 'zh', 'en', 'ja').
                - source_lang: Source language code (auto-detect if not set).
                - style: Translation style (formal, informal, technical).

        Returns:
            ToolResult with translated text.
        """
        target_lang = kwargs.get("target_lang", "en")
        source_lang = kwargs.get("source_lang", "")
        style = kwargs.get("style", "")

        target_name = LANGUAGE_MAP.get(target_lang, target_lang)
        source_name = LANGUAGE_MAP.get(source_lang, source_lang) if source_lang else "auto-detect"

        user_prompt = f"Translate the following text to {target_name}."
        if source_lang:
            user_prompt += f" Source language: {source_name}."
        if style:
            user_prompt += f" Style: {style}."
        user_prompt += f"\n\nText:\n{input_data}"

        response = await self.provider.complete_with_system(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=response.content,
            metadata={
                "source_lang": source_name,
                "target_lang": target_name,
                "model": response.model,
            },
            tokens_used=response.total_tokens,
        )
