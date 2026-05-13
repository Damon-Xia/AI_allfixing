"""Tests for Code Fixer tool."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ai_allfixing.tools.code_fixer import CodeFixer


class TestCodeFixer:
    """Tests for CodeFixer."""

    def setup_method(self) -> None:
        self.tool = CodeFixer(provider=MagicMock())

    def test_validate_input_valid(self) -> None:
        self.tool.validate_input("def foo(): pass")

    def test_validate_input_empty(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            self.tool.validate_input("")

    def test_validate_input_whitespace(self) -> None:
        with pytest.raises(ValueError, match="cannot be empty"):
            self.tool.validate_input("   \n  ")

    def test_validate_input_not_string(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            self.tool.validate_input(123)

    @pytest.mark.asyncio
    async def test_execute(self, mock_provider: MagicMock) -> None:
        tool = CodeFixer(provider=mock_provider)
        result = await tool.run("def foo()\n  pass")
        assert result.success
        assert result.output == "Mock system response"
        mock_provider.complete_with_system.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_language(self, mock_provider: MagicMock) -> None:
        tool = CodeFixer(provider=mock_provider)
        result = await tool.run("function foo() {}", language="javascript")
        assert result.success
        call_kwargs = mock_provider.complete_with_system.call_args
        assert "javascript" in call_kwargs.kwargs.get("user_prompt", "") or "javascript" in str(call_kwargs)
