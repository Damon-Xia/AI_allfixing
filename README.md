<p align="center">
  <img src="docs/assets/logo.png" alt="AI AllFixing Logo" width="200"/>
</p>

<h1 align="center">AI AllFixing</h1>

<p align="center">
  <strong>A powerful collection of AI-powered tools to fix, enhance, and automate everything.</strong>
</p>

<p align="center">
  <a href="https://github.com/Damon-Xia/AI_allfixing/actions"><img src="https://github.com/Damon-Xia/AI_allfixing/workflows/CI/badge.svg" alt="CI Status"></a>
  <a href="https://pypi.org/project/ai-allfixing/"><img src="https://img.shields.io/pypi/v/ai-allfixing.svg" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/ai-allfixing/"><img src="https://img.shields.io/pypi/pyversions/ai-allfixing.svg" alt="Python Versions"></a>
  <a href="https://github.com/Damon-Xia/AI_allfixing/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Damon-Xia/AI_allfixing.svg" alt="License"></a>
  <a href="https://github.com/Damon-Xia/AI_allfixing/stargazers"><img src="https://img.shields.io/github/stars/Damon-Xia/AI_allfixing.svg?style=social" alt="GitHub Stars"></a>
</p>

---

## Features

- **Code Fixer** - Automatically detect and fix bugs, syntax errors, and code smells using AI
- **Text Summarizer** - Summarize long documents, articles, and text into concise key points
- **Translator** - AI-powered translation supporting 50+ languages with context awareness
- **Code Reviewer** - Get instant AI code reviews with actionable suggestions
- **Doc Generator** - Auto-generate documentation from source code
- **Shell Assistant** - Natural language to shell commands conversion

## Quick Start

### Installation

```bash
pip install ai-allfixing
```

Or install from source:

```bash
git clone https://github.com/Damon-Xia/AI_allfixing.git
cd AI_allfixing
pip install -e ".[dev]"
```

### Configuration

Set your API key:

```bash
export OPENAI_API_KEY="your-api-key"
# Or use the config command
ai-fix config set api_key YOUR_KEY
```

### Usage

#### Command Line

```bash
# Fix code in a file
ai-fix code fix buggy_script.py

# Summarize a document
ai-fix text summarize long_article.txt

# Translate text
ai-fix text translate "Hello, World!" --target zh

# Review code
ai-fix code review my_module.py

# Generate docs
ai-fix docs generate ./src

# Natural language to shell
ai-fix shell "find all python files modified in the last 7 days"
```

#### Python API

```python
from ai_allfixing import CodeFixer, TextSummarizer, Translator

# Fix code
fixer = CodeFixer()
fixed_code = await fixer.run("def add(a, b)\n  return a + b")
print(fixed_code.output)

# Summarize text
summarizer = TextSummarizer()
summary = await summarizer.run(long_text, max_length=100)

# Translate
translator = Translator()
result = await translator.run("Hello, World!", target_lang="zh")
print(result.output)  # "你好，世界！"
```

## Supported AI Providers

| Provider | Models | Status |
|----------|--------|--------|
| OpenAI | GPT-4o, GPT-4, GPT-3.5 | Supported |
| Anthropic | Claude 3.5, Claude 3 | Supported |
| Local Models | Ollama, vLLM | Supported |
| Azure OpenAI | All Azure models | Supported |

## Project Structure

```
AI_allfixing/
├── src/ai_allfixing/       # Core package
│   ├── core/               # Core engine and base classes
│   ├── tools/              # AI tool implementations
│   ├── providers/          # LLM provider integrations
│   ├── cli/                # Command-line interface
│   └── utils/              # Shared utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Usage examples
└── configs/                # Configuration templates
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Configuration Guide](docs/configuration.md)
- [API Reference](docs/api-reference.md)
- [Adding Custom Tools](docs/custom-tools.md)
- [Provider Setup](docs/providers.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Roadmap

- [x] Core framework and plugin system
- [x] Code Fixer tool
- [x] Text Summarizer tool
- [x] Translator tool
- [ ] Image analysis and description
- [ ] Audio transcription and processing
- [ ] RAG (Retrieval-Augmented Generation) tool
- [ ] Web scraping with AI extraction
- [ ] PDF parsing and intelligent Q&A
- [ ] VS Code extension
- [ ] Web UI dashboard

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Damon-Xia/AI_allfixing&type=Date)](https://star-history.com/#Damon-Xia/AI_allfixing&Date)

---

<p align="center">Made with ❤️ by <a href="https://github.com/Damon-Xia">Damon Xia</a> and contributors</p>
