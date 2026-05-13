"""Tests for Text Summarizer tool."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ai_allfixing.tools.summarizer import TextSummarizer


class TestTextSummarizer:
    """Tests for TextSummarizer."""

    def setup_method(self) -> None:
        self.tool = TextSummarizer(provider=MagicMock())

    def test_validate_input_valid(self) -> None:
        self.tool.validate_input("Some long text to summarize")

    def test_validate_input_empty(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            self.tool.validate_input("")

    def test_validate_input_not_string(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            self.tool.validate_input([1, 2, 3])

    @pytest.mark.asyncio
    async def test_execute(self, mock_provider: MagicMock) -> None:
        tool = TextSummarizer(provider=mock_provider)
        long_text = "This is a long article " * 100
        result = await tool.run(long_text, max_length=50, format="bullets")
        assert result.success
        assert result.metadata["format"] == "bullets"
        mock_provider.complete_with_system.assert_called_once()
