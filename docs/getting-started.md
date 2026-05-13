# Getting Started

Welcome to AI AllFixing! This guide will help you get up and running quickly.

## Prerequisites

- Python 3.9 or higher
- An API key from a supported provider (OpenAI, Anthropic, etc.)

## Installation

### From PyPI (Recommended)

```bash
pip install ai-allfixing
```

### From Source

```bash
git clone https://github.com/Damon-Xia/AI_allfixing.git
cd AI_allfixing
pip install -e ".[dev]"
```

## Configuration

### 1. Set Your API Key

The easiest way is via environment variable:

```bash
# For OpenAI
export OPENAI_API_KEY="sk-your-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Or use the config command:

```bash
ai-fix config set provider.api_key YOUR_KEY
```

### 2. Choose Your Provider

```bash
# Use OpenAI (default)
ai-fix config set provider.name openai
ai-fix config set provider.model gpt-4o

# Use Anthropic
ai-fix config set provider.name anthropic
ai-fix config set provider.model claude-sonnet-4-20250514
```

### 3. Verify Setup

```bash
ai-fix config show
```

## Your First Commands

### Fix Some Code

```bash
# Create a file with a bug
echo 'def add(a, b)
  return a + b' > buggy.py

# Fix it!
ai-fix code fix buggy.py
```

### Translate Text

```bash
ai-fix text translate "Hello, how are you?" --target zh
```

### Get a Shell Command

```bash
ai-fix shell "list all files larger than 100MB"
```

## Using as a Python Library

```python
import asyncio
from ai_allfixing import CodeFixer, Config

async def main():
    fixer = CodeFixer()
    result = await fixer.run("def broken(:\n  pass")
    print(result.output)

asyncio.run(main())
```

## Next Steps

- [Configuration Guide](configuration.md) - Advanced configuration options
- [API Reference](api-reference.md) - Full API documentation
- [Custom Tools](custom-tools.md) - Build your own tools
- [Provider Setup](providers.md) - Configure different AI providers
