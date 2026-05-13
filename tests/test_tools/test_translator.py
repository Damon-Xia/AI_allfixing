"""Tests for Translator tool."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ai_allfixing.tools.translator import Translator, LANGUAGE_MAP


class TestTranslator:
    """Tests for Translator."""

    def setup_method(self) -> None:
        self.tool = Translator(provider=MagicMock())

    def test_validate_input_valid(self) -> None:
        self.tool.validate_input("Hello, World!")

    def test_validate_input_empty(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            self.tool.validate_input("")

    def test_validate_input_not_string(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            self.tool.validate_input(42)

    def test_language_map(self) -> None:
        assert "zh" in LANGUAGE_MAP
        assert "en" in LANGUAGE_MAP
        assert "ja" in LANGUAGE_MAP

    @pytest.mark.asyncio
    async def test_execute(self, mock_provider: MagicMock) -> None:
        tool = Translator(provider=mock_provider)
        result = await tool.run("Hello", target_lang="zh")
        assert result.success
        assert result.metadata["target_lang"] == "Chinese (Simplified)"
        mock_provider.complete_with_system.assert_called_once()
