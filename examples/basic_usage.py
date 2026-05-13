"""Basic usage examples for AI AllFixing.

Make sure to set your API key before running:
    export OPENAI_API_KEY="your-key"
"""

import asyncio

from ai_allfixing import CodeFixer, TextSummarizer, Translator


async def fix_code_example() -> None:
    """Example: Fix buggy Python code."""
    print("=" * 50)
    print("Example 1: Code Fixer")
    print("=" * 50)

    buggy_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers
        total += num
    return total / len(numbers)
"""

    fixer = CodeFixer()
    result = await fixer.run(buggy_code, language="python")

    if result.success:
        print("Fixed code:")
        print(result.output)
        print(f"\nTokens used: {result.tokens_used}")
    else:
        print(f"Error: {result.error}")


async def summarize_text_example() -> None:
    """Example: Summarize a long text."""
    print("\n" + "=" * 50)
    print("Example 2: Text Summarizer")
    print("=" * 50)

    long_text = """
    Artificial intelligence (AI) has rapidly evolved from a niche research field into one
    of the most transformative technologies of the 21st century. Machine learning, a subset
    of AI, enables systems to learn and improve from experience without being explicitly
    programmed. Deep learning, which uses neural networks with many layers, has achieved
    remarkable breakthroughs in image recognition, natural language processing, and game
    playing. The development of large language models (LLMs) like GPT-4 has opened up new
    possibilities for human-computer interaction, enabling AI systems to understand and
    generate human language with unprecedented fluency. These advances have led to practical
    applications in healthcare, finance, transportation, and education, promising to
    revolutionize how we work and live.
    """

    summarizer = TextSummarizer()
    result = await summarizer.run(long_text, max_length=50, format="bullets")

    if result.success:
        print("Summary:")
        print(result.output)
    else:
        print(f"Error: {result.error}")


async def translate_text_example() -> None:
    """Example: Translate text between languages."""
    print("\n" + "=" * 50)
    print("Example 3: Translator")
    print("=" * 50)

    text = "The quick brown fox jumps over the lazy dog."

    translator = Translator()

    # Translate to Chinese
    result = await translator.run(text, target_lang="zh")
    if result.success:
        print(f"English -> Chinese: {result.output}")

    # Translate to Japanese
    result = await translator.run(text, target_lang="ja")
    if result.success:
        print(f"English -> Japanese: {result.output}")

    # Translate to Spanish
    result = await translator.run(text, target_lang="es")
    if result.success:
        print(f"English -> Spanish: {result.output}")


async def main() -> None:
    """Run all examples."""
    await fix_code_example()
    await summarize_text_example()
    await translate_text_example()


if __name__ == "__main__":
    asyncio.run(main())
