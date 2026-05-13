"""Tests for base classes."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from ai_allfixing.core.base import BaseTool, ToolResult, ToolStatus


class DummyTool(BaseTool):
    """A dummy tool for testing."""

    name = "dummy"
    description = "A test tool"

    def validate_input(self, input_data: Any) -> None:
        if not input_data:
            raise ValueError("Input cannot be empty")

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Processed: {input_data}",
            tokens_used=10,
        )


class FailingTool(BaseTool):
    """A tool that always fails."""

    name = "failing"
    description = "Always fails"

    def validate_input(self, input_data: Any) -> None:
        pass

    async def execute(self, input_data: Any, **kwargs: Any) -> ToolResult:
        raise RuntimeError("Something went wrong")


class TestToolResult:
    """Tests for ToolResult."""

    def test_success_result(self) -> None:
        result = ToolResult(status=ToolStatus.SUCCESS, output="hello")
        assert result.success is True
        assert result.output == "hello"
        assert result.error is None

    def test_error_result(self) -> None:
        result = ToolResult(status=ToolStatus.ERROR, output="", error="failed")
        assert result.success is False
        assert result.error == "failed"

    def test_to_dict(self) -> None:
        result = ToolResult(
            status=ToolStatus.SUCCESS,
            output="test",
            tokens_used=42,
            metadata={"key": "value"},
        )
        d = result.to_dict()
        assert d["status"] == "success"
        assert d["output"] == "test"
        assert d["tokens_used"] == 42
        assert d["metadata"] == {"key": "value"}


class TestBaseTool:
    """Tests for BaseTool."""

    @pytest.mark.asyncio
    async def test_run_success(self) -> None:
        tool = DummyTool(provider=MagicMock())
        result = await tool.run("test input")
        assert result.success
        assert result.output == "Processed: test input"

    @pytest.mark.asyncio
    async def test_run_validation_error(self) -> None:
        tool = DummyTool(provider=MagicMock())
        result = await tool.run("")
        assert not result.success
        assert "Validation error" in (result.error or "")

    @pytest.mark.asyncio
    async def test_run_execution_error(self) -> None:
        tool = FailingTool(provider=MagicMock())
        result = await tool.run("anything")
        assert not result.success
        assert "Execution error" in (result.error or "")

    def test_repr(self) -> None:
        tool = DummyTool(provider=MagicMock())
        assert "DummyTool" in repr(tool)
        assert "dummy" in repr(tool)
