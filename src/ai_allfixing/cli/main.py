"""Main CLI entry point for AI AllFixing."""

from __future__ import annotations

import click
from rich.console import Console

from ai_allfixing import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="ai-fix")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic"]),
    default=None,
    help="LLM provider to use.",
)
@click.option("--model", "-m", default=None, help="Model name to use.")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, provider: str | None, model: str | None) -> None:
    """AI AllFixing - AI-powered tools to fix, enhance, and automate everything.

    Use 'ai-fix <command> --help' for more information on a specific command.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["provider"] = provider
    ctx.obj["model"] = model


@cli.group()
def code() -> None:
    """Code-related tools (fix, review)."""


@cli.group()
def text() -> None:
    """Text-related tools (summarize, translate)."""


@cli.group()
def docs() -> None:
    """Documentation tools (generate)."""


@cli.command()
@click.argument("description", nargs=-1, required=True)
@click.option("--os", "target_os", default="linux", help="Target OS.")
@click.option("--shell", "target_shell", default="bash", help="Target shell.")
@click.pass_context
def shell(ctx: click.Context, description: tuple[str, ...], target_os: str, target_shell: str) -> None:
    """Convert natural language to shell commands.

    Example: ai-fix shell "find all python files modified in the last 7 days"
    """
    import asyncio

    from ai_allfixing.tools.shell_assistant import ShellAssistant
    from ai_allfixing.cli._helpers import get_config

    config = get_config(ctx)
    tool = ShellAssistant(config=config)
    text_input = " ".join(description)

    result = asyncio.run(tool.run(text_input, os=target_os, shell=target_shell))

    if result.success:
        console.print(result.output)
    else:
        console.print(f"[red]Error:[/red] {result.error}")


@code.command("fix")
@click.argument("file", type=click.Path(exists=True))
@click.option("--language", "-l", default="", help="Programming language hint.")
@click.option("--explain", is_flag=True, help="Include explanation of changes.")
@click.option("--output", "-o", default=None, help="Output file (default: overwrite input).")
@click.pass_context
def code_fix(ctx: click.Context, file: str, language: str, explain: bool, output: str | None) -> None:
    """Fix bugs and errors in a code file.

    Example: ai-fix code fix buggy_script.py
    """
    import asyncio

    from ai_allfixing.tools.code_fixer import CodeFixer
    from ai_allfixing.utils.helpers import read_file, write_file
    from ai_allfixing.cli._helpers import get_config

    config = get_config(ctx)
    tool = CodeFixer(config=config)
    source = read_file(file)

    with console.status("[bold green]Fixing code..."):
        result = asyncio.run(tool.run(source, language=language, explain=explain))

    if result.success:
        output_path = output or file
        write_file(output_path, result.output)
        console.print(f"[green]Fixed code written to:[/green] {output_path}")
        if ctx.obj.get("verbose"):
            console.print(f"[dim]Tokens used: {result.tokens_used}[/dim]")
    else:
        console.print(f"[red]Error:[/red] {result.error}")


@code.command("review")
@click.argument("file", type=click.Path(exists=True))
@click.option("--language", "-l", default="", help="Programming language hint.")
@click.option("--focus", "-f", default="all", type=click.Choice(["all", "security", "performance", "style"]))
@click.pass_context
def code_review(ctx: click.Context, file: str, language: str, focus: str) -> None:
    """Review a code file and provide feedback.

    Example: ai-fix code review my_module.py
    """
    import asyncio

    from ai_allfixing.tools.code_reviewer import CodeReviewer
    from ai_allfixing.utils.helpers import read_file
    from ai_allfixing.cli._helpers import get_config

    config = get_config(ctx)
    tool = CodeReviewer(config=config)
    source = read_file(file)

    with console.status("[bold green]Reviewing code..."):
        result = asyncio.run(tool.run(source, language=language, focus=focus))

    if result.success:
        console.print(result.output)
    else:
        console.print(f"[red]Error:[/red] {result.error}")


@text.command("summarize")
@click.argument("file", type=click.Path(exists=True))
@click.option("--max-length", default=200, help="Maximum summary word count.")
@click.option("--format", "fmt", default="bullets", type=click.Choice(["bullets", "paragraph", "one_line"]))
@click.pass_context
def text_summarize(ctx: click.Context, file: str, max_length: int, fmt: str) -> None:
    """Summarize a text file.

    Example: ai-fix text summarize long_article.txt
    """
    import asyncio

    from ai_allfixing.tools.summarizer import TextSummarizer
    from ai_allfixing.utils.helpers import read_file
    from ai_allfixing.cli._helpers import get_config

    config = get_config(ctx)
    tool = TextSummarizer(config=config)
    source = read_file(file)

    with console.status("[bold green]Summarizing..."):
        result = asyncio.run(tool.run(source, max_length=max_length, format=fmt))

    if result.success:
        console.print(result.output)
    else:
        console.print(f"[red]Error:[/red] {result.error}")


@text.command("translate")
@click.argument("text_input")
@click.option("--target", "-t", default="en", help="Target language code (e.g., zh, en, ja).")
@click.option("--source", "-s", default="", help="Source language code (auto-detect if empty).")
@click.pass_context
def text_translate(ctx: click.Context, text_input: str, target: str, source: str) -> None:
    """Translate text to another language.

    Example: ai-fix text translate "Hello, World!" --target zh
    """
    import asyncio
    from pathlib import Path

    from ai_allfixing.tools.translator import Translator
    from ai_allfixing.cli._helpers import get_config

    config = get_config(ctx)
    tool = Translator(config=config)

    # If input looks like a file path, read the file
    if Path(text_input).exists():
        text_input = Path(text_input).read_text(encoding="utf-8")

    with console.status("[bold green]Translating..."):
        result = asyncio.run(tool.run(text_input, target_lang=target, source_lang=source))

    if result.success:
        console.print(result.output)
    else:
        console.print(f"[red]Error:[/red] {result.error}")


@docs.command("generate")
@click.argument("path", type=click.Path(exists=True))
@click.option("--style", default="google", type=click.Choice(["google", "numpy", "sphinx"]))
@click.option("--output-type", default="docstring", type=click.Choice(["docstring", "readme", "api"]))
@click.pass_context
def docs_generate(ctx: click.Context, path: str, style: str, output_type: str) -> None:
    """Generate documentation from source code.

    Example: ai-fix docs generate ./src
    """
    import asyncio
    from pathlib import Path as FilePath

    from ai_allfixing.tools.doc_generator import DocGenerator
    from ai_allfixing.utils.helpers import read_file
    from ai_allfixing.cli._helpers import get_config

    config = get_config(ctx)
    tool = DocGenerator(config=config)

    target = FilePath(path)
    if target.is_file():
        source = read_file(path)
    else:
        # Concatenate all Python files in directory
        files = sorted(target.rglob("*.py"))
        parts = []
        for f in files[:20]:  # Limit to 20 files
            parts.append(f"# --- {f.relative_to(target)} ---\n{f.read_text(encoding='utf-8')}")
        source = "\n\n".join(parts)

    with console.status("[bold green]Generating docs..."):
        result = asyncio.run(tool.run(source, style=style, output_type=output_type))

    if result.success:
        console.print(result.output)
    else:
        console.print(f"[red]Error:[/red] {result.error}")


@cli.command("config")
@click.argument("action", type=click.Choice(["set", "get", "show"]))
@click.argument("key", required=False)
@click.argument("value", required=False)
def config_cmd(action: str, key: str | None, value: str | None) -> None:
    """Manage configuration.

    Examples:
        ai-fix config show
        ai-fix config set provider.model gpt-4o
        ai-fix config get provider.model
    """
    from ai_allfixing.core.config import Config

    config = Config.from_file()

    if action == "show":
        console.print("[bold]Current Configuration:[/bold]")
        console.print(f"  Provider: {config.provider.name}")
        console.print(f"  Model: {config.provider.model}")
        console.print(f"  Max Tokens: {config.provider.max_tokens}")
        console.print(f"  Temperature: {config.provider.temperature}")
        console.print(f"  API Key: {'***' + config.provider.api_key[-4:] if config.provider.api_key else '[not set]'}")
        console.print(f"  Log Level: {config.log_level}")
        console.print(f"  Cache: {'enabled' if config.cache_enabled else 'disabled'}")
    elif action == "get":
        if not key:
            console.print("[red]Error: key is required for 'get'[/red]")
            return
        try:
            val = config.get(key)
            console.print(f"{key} = {val}")
        except KeyError as e:
            console.print(f"[red]Error:[/red] {e}")
    elif action == "set":
        if not key or value is None:
            console.print("[red]Error: key and value are required for 'set'[/red]")
            return
        try:
            config.set(key, value)
            config.save()
            console.print(f"[green]Set {key} = {value}[/green]")
        except KeyError as e:
            console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    cli()
