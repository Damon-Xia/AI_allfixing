# API Reference

Complete API reference for the AI AllFixing Python library.

## Core

### `Config`

```python
from ai_allfixing import Config

config = Config()
config = Config.from_file("path/to/config.yaml")
config.save("path/to/config.yaml")
config.set("provider.model", "gpt-4o")
value = config.get("provider.model")
```

### `Engine`

```python
from ai_allfixing.core import Engine, Config

engine = Engine(config=Config())
provider = engine.get_provider()          # Default provider
provider = engine.get_provider("anthropic")  # Specific provider
result = await engine.run_tool(tool, input_data)
```

## Tools

All tools follow the same interface pattern:

```python
tool = ToolClass(config=config, provider=provider)
result = await tool.run(input_data, **options)
```

### `CodeFixer`

Automatically detect and fix bugs, syntax errors, and code smells.

```python
from ai_allfixing import CodeFixer

fixer = CodeFixer()
result = await fixer.run(
    code_string,
    language="python",  # Optional language hint
    explain=True,       # Include explanation
)
print(result.output)    # Fixed code
```

### `TextSummarizer`

Summarize long documents into concise key points.

```python
from ai_allfixing import TextSummarizer

summarizer = TextSummarizer()
result = await summarizer.run(
    long_text,
    max_length=200,       # Max words
    format="bullets",     # bullets, paragraph, one_line
    language="en",        # Output language
)
print(result.output)
```

### `Translator`

AI-powered translation supporting 50+ languages.

```python
from ai_allfixing import Translator

translator = Translator()
result = await translator.run(
    "Hello, World!",
    target_lang="zh",     # Target language code
    source_lang="",       # Auto-detect if empty
    style="formal",       # formal, informal, technical
)
print(result.output)      # "你好，世界！"
```

### `CodeReviewer`

Get instant AI code reviews with actionable suggestions.

```python
from ai_allfixing import CodeReviewer

reviewer = CodeReviewer()
result = await reviewer.run(
    source_code,
    language="python",
    focus="security",     # all, security, performance, style
    context="Auth module",
)
print(result.output)      # Structured review
```

### `DocGenerator`

Auto-generate documentation from source code.

```python
from ai_allfixing import DocGenerator

doc_gen = DocGenerator()
result = await doc_gen.run(
    source_code,
    style="google",        # google, numpy, sphinx
    output_type="docstring",  # docstring, readme, api
    language="python",
)
print(result.output)
```

### `ShellAssistant`

Natural language to shell commands conversion.

```python
from ai_allfixing import ShellAssistant

shell = ShellAssistant()
result = await shell.run(
    "find all python files modified today",
    os="linux",
    shell="bash",
    safe_mode=True,
)
print(result.output)
```

## ToolResult

All tools return a `ToolResult`:

```python
result = await tool.run(input_data)

result.success       # bool - was it successful?
result.status        # ToolStatus enum (SUCCESS, ERROR, PARTIAL)
result.output        # str - main output
result.error         # str | None - error message
result.tokens_used   # int - tokens consumed
result.metadata      # dict - additional info
result.to_dict()     # dict - serialize to dict
```

## Providers

### `OpenAIProvider`

```python
from ai_allfixing.providers import OpenAIProvider
from ai_allfixing.core.config import ProviderConfig

config = ProviderConfig(name="openai", api_key="sk-...", model="gpt-4o")
provider = OpenAIProvider(config=config)

response = await provider.complete("Hello!")
response = await provider.complete_with_system("You are helpful.", "Hello!")
```

### `AnthropicProvider`

```python
from ai_allfixing.providers import AnthropicProvider
from ai_allfixing.core.config import ProviderConfig

config = ProviderConfig(name="anthropic", api_key="sk-ant-...", model="claude-sonnet-4-20250514")
provider = AnthropicProvider(config=config)

response = await provider.complete("Hello!")
```

### `CompletionResponse`

```python
response.content        # str - response text
response.model          # str - model used
response.tokens_input   # int - input tokens
response.tokens_output  # int - output tokens
response.total_tokens   # int - total tokens (property)
response.finish_reason  # str - stop reason
response.raw            # Any - raw API response
```
