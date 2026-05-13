"""Tests for utility helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_allfixing.utils.helpers import (
    count_tokens,
    detect_language,
    format_output,
    read_file,
    truncate_text,
    write_file,
)


class TestCountTokens:
    """Tests for count_tokens."""

    def test_empty_string(self) -> None:
        assert count_tokens("") == 0

    def test_non_empty_string(self) -> None:
        result = count_tokens("Hello, world!")
        assert result > 0


class TestReadWriteFile:
    """Tests for read_file and write_file."""

    def test_write_and_read(self, tmp_path: Path) -> None:
        file_path = tmp_path / "test.txt"
        write_file(file_path, "Hello, World!")
        content = read_file(file_path)
        assert content == "Hello, World!"

    def test_read_nonexistent(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_file(tmp_path / "nonexistent.txt")

    def test_write_creates_dirs(self, tmp_path: Path) -> None:
        file_path = tmp_path / "deep" / "nested" / "file.txt"
        write_file(file_path, "content")
        assert file_path.exists()
        assert read_file(file_path) == "content"


class TestTruncateText:
    """Tests for truncate_text."""

    def test_short_text(self) -> None:
        assert truncate_text("short", max_length=100) == "short"

    def test_long_text(self) -> None:
        long = "a" * 200
        result = truncate_text(long, max_length=50)
        assert len(result) <= 50
        assert result.endswith("[truncated]")


class TestDetectLanguage:
    """Tests for detect_language."""

    def test_python(self) -> None:
        code = "def hello():\n    print('hello')\n    self.value = 1"
        assert detect_language(code) == "python"

    def test_javascript(self) -> None:
        code = "const foo = () => {\n  console.log('hi');\n};"
        assert detect_language(code) == "javascript"

    def test_unknown(self) -> None:
        assert detect_language("random text without code patterns") == "unknown"


class TestFormatOutput:
    """Tests for format_output."""

    def test_text_format(self) -> None:
        assert format_output("hello", "text") == "hello"

    def test_json_format(self) -> None:
        result = format_output("hello", "json")
        assert '"result"' in result
        assert '"hello"' in result

    def test_markdown_format(self) -> None:
        result = format_output("code here", "markdown")
        assert "```" in result
