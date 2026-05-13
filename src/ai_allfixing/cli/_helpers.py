"""CLI helper utilities."""

from __future__ import annotations

import click

from ai_allfixing.core.config import Config


def get_config(ctx: click.Context) -> Config:
    """Build a Config from CLI context options.

    Args:
        ctx: Click context with obj dict.

    Returns:
        Config instance with CLI overrides applied.
    """
    config = Config.from_file()

    provider = ctx.obj.get("provider")
    model = ctx.obj.get("model")

    if provider:
        config.provider.name = provider
    if model:
        config.provider.model = model

    return config
