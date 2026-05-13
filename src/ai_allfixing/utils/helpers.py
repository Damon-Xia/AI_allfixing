"""Shared utility functions."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count the number of tokens in a text string.

    Args:
        text: The text to count tokens for.
        model: The model to use for tokenization.

    Returns:
        Number of tokens.
    """
    try:
        import tiktoken

        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 chars for English)
        return len(text) // 4


def read_file(path: str | Path) -> str:
    """Read a file and return its contents.

    Args:
        path: Path to the file.

    Returns:
        File contents as string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        IOError: If file cannot be read.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return file_path.read_text(encoding="utf-8")


def write_file(path: str | Path, content: str) -> None:
    """Write content to a file, creating parent directories if needed.

    Args:
        path: Path to the file.
        content: Content to write.
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def truncate_text(text: str, max_length: int = 10000, suffix: str = "\n... [truncated]") -> str:
    """Truncate text to a maximum length.

    Args:
        text: Text to truncate.
        max_length: Maximum character length.
        suffix: String to append when truncated.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def detect_language(code: str) -> str:
    """Attempt to detect the programming language of a code snippet.

    Uses simple heuristics based on syntax patterns.

    Args:
        code: Source code string.

    Returns:
        Detected language name or "unknown".
    """
    indicators: dict[str, list[str]] = {
        "python": ["def ", "import ", "class ", "elif ", "self.", "print("],
        "javascript": ["const ", "let ", "function ", "=>", "console.log"],
        "typescript": ["interface ", ": string", ": number", "export ", "import type"],
        "java": ["public class", "public static void", "System.out", "import java"],
        "go": ["func ", "package ", "import (", "fmt."],
        "rust": ["fn ", "let mut", "impl ", "use ", "pub fn"],
        "c": ["#include", "int main(", "printf(", "malloc("],
        "cpp": ["#include", "std::", "cout", "namespace", "template<"],
    }

    code_lower = code.lower()
    scores: dict[str, int] = {}

    for lang, patterns in indicators.items():
        score = sum(1 for p in patterns if p.lower() in code_lower)
        if score > 0:
            scores[lang] = score

    if not scores:
        return "unknown"

    return max(scores, key=scores.get)  # type: ignore[arg-type]


def format_output(data: Any, fmt: str = "text") -> str:
    """Format output data in the specified format.

    Args:
        data: Data to format.
        fmt: Output format (text, json, markdown).

    Returns:
        Formatted string.
    """
    if fmt == "json":
        import json

        if isinstance(data, str):
            return json.dumps({"result": data}, indent=2, ensure_ascii=False)
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    elif fmt == "markdown":
        if isinstance(data, str):
            return f"```\n{data}\n```"
        return str(data)
    else:
        return str(data)
