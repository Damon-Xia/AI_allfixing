"""Example: Code Review and Documentation Generation.

Shows how to use the CodeReviewer and DocGenerator tools.
"""

import asyncio

from ai_allfixing import CodeReviewer, DocGenerator


SAMPLE_CODE = '''
import os
import sys

def process_data(data, output_file):
    """Process data and write to file."""
    results = []
    for item in data:
        if item['type'] == 'A':
            value = item['value'] * 2
            results.append(value)
        elif item['type'] == 'B':
            value = item['value'] + 10
            results.append(value)

    f = open(output_file, 'w')
    for r in results:
        f.write(str(r) + '\\n')
    # Bug: file never closed!

    return results


def calculate(x, y, operation='add'):
    if operation == 'add':
        return x + y
    elif operation == 'subtract':
        return x - y
    elif operation == 'divide':
        return x / y  # Bug: no zero division check
    elif operation == 'multiply':
        return x * y
'''


async def review_code() -> None:
    """Get an AI code review."""
    print("=" * 60)
    print("Code Review")
    print("=" * 60)

    reviewer = CodeReviewer()
    result = await reviewer.run(
        SAMPLE_CODE,
        language="python",
        focus="all",
        context="Data processing utility module",
    )

    if result.success:
        print(result.output)
    else:
        print(f"Error: {result.error}")


async def generate_docs() -> None:
    """Generate documentation."""
    print("\n" + "=" * 60)
    print("Generated Documentation")
    print("=" * 60)

    doc_gen = DocGenerator()
    result = await doc_gen.run(
        SAMPLE_CODE,
        style="google",
        output_type="docstring",
        language="python",
    )

    if result.success:
        print(result.output)
    else:
        print(f"Error: {result.error}")


async def main() -> None:
    """Run examples."""
    await review_code()
    await generate_docs()


if __name__ == "__main__":
    asyncio.run(main())
