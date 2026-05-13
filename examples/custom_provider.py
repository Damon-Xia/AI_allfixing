"""Example: Using different AI providers.

This example shows how to configure and switch between providers.
"""

import asyncio

from ai_allfixing import CodeFixer, Config
from ai_allfixing.core.config import ProviderConfig


async def use_openai() -> None:
    """Use OpenAI GPT-4o."""
    print("Using OpenAI GPT-4o...")

    config = Config(
        provider=ProviderConfig(
            name="openai",
            model="gpt-4o",
            temperature=0.0,
        )
    )

    fixer = CodeFixer(config=config)
    result = await fixer.run("def foo(x)\n  return x + 1")

    if result.success:
        print(f"Result ({result.metadata.get('model', 'unknown')}):")
        print(result.output)


async def use_anthropic() -> None:
    """Use Anthropic Claude."""
    print("\nUsing Anthropic Claude...")

    config = Config(
        provider=ProviderConfig(
            name="anthropic",
            model="claude-sonnet-4-20250514",
            temperature=0.0,
        )
    )

    fixer = CodeFixer(config=config)
    result = await fixer.run("def foo(x)\n  return x + 1")

    if result.success:
        print(f"Result ({result.metadata.get('model', 'unknown')}):")
        print(result.output)


async def use_local_ollama() -> None:
    """Use a local Ollama model."""
    print("\nUsing local Ollama model...")

    config = Config(
        provider=ProviderConfig(
            name="openai",  # Ollama is OpenAI-compatible
            model="llama3",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
    )

    fixer = CodeFixer(config=config)
    result = await fixer.run("def foo(x)\n  return x + 1")

    if result.success:
        print(f"Result:")
        print(result.output)


async def main() -> None:
    """Run provider examples."""
    await use_openai()
    # Uncomment if you have Anthropic key:
    # await use_anthropic()
    # Uncomment if you have Ollama running:
    # await use_local_ollama()


if __name__ == "__main__":
    asyncio.run(main())
