"""Logging configuration for AI AllFixing."""

from __future__ import annotations

import logging
import sys


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__).
        level: Log level string.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(f"ai_allfixing.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
