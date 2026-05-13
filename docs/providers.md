# Provider Setup Guide

AI AllFixing supports multiple LLM providers. This guide covers setup for each.

## OpenAI

### Setup

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the environment variable:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Available Models

| Model | Best For | Cost |
|-------|----------|------|
| gpt-4o | Best quality, multimodal | $$$ |
| gpt-4o-mini | Fast, cost-effective | $ |
| gpt-4 | High quality text | $$ |
| gpt-3.5-turbo | Basic tasks, cheapest | $ |

### Configuration

```yaml
provider:
  name: openai
  model: gpt-4o
  max_tokens: 4096
  temperature: 0.1
```

## Anthropic (Claude)

### Setup

1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Set the environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### Available Models

| Model | Best For | Cost |
|-------|----------|------|
| claude-sonnet-4-20250514 | Best balance of speed/quality | $$ |
| claude-3-opus | Highest quality | $$$ |
| claude-3-haiku | Fastest, cheapest | $ |

### Configuration

```yaml
provider:
  name: anthropic
  model: claude-sonnet-4-20250514
  max_tokens: 4096
  temperature: 0.1
```

## Azure OpenAI

### Setup

1. Create an Azure OpenAI resource
2. Deploy a model
3. Get your endpoint and key

```bash
export AZURE_OPENAI_API_KEY="your-key"
```

### Configuration

```yaml
provider:
  name: openai
  model: your-deployment-name
  base_url: https://your-resource.openai.azure.com/openai/deployments/your-deployment
  extra:
    api_version: "2024-02-01"
```

## Local Models (Ollama)

### Setup

1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull llama3`
3. Start the server: `ollama serve`

### Configuration

```yaml
provider:
  name: openai  # Ollama is OpenAI-compatible
  model: llama3
  base_url: http://localhost:11434/v1
  api_key: ollama  # Any non-empty string works
```

## Local Models (vLLM)

### Setup

1. Install vLLM: `pip install vllm`
2. Start the server:

```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-8b-instruct \
    --port 8000
```

### Configuration

```yaml
provider:
  name: openai
  model: meta-llama/Llama-3-8b-instruct
  base_url: http://localhost:8000/v1
  api_key: local
```

## Switching Providers

### Via CLI

```bash
# One-time override
ai-fix --provider anthropic --model claude-sonnet-4-20250514 code fix file.py

# Permanent change
ai-fix config set provider.name anthropic
ai-fix config set provider.model claude-sonnet-4-20250514
```

### Via Python

```python
from ai_allfixing import Config, CodeFixer
from ai_allfixing.core.config import ProviderConfig

config = Config(
    provider=ProviderConfig(
        name="anthropic",
        model="claude-sonnet-4-20250514",
    )
)
fixer = CodeFixer(config=config)
```

## Provider Comparison

| Feature | OpenAI | Anthropic | Local |
|---------|--------|-----------|-------|
| Quality | Excellent | Excellent | Varies |
| Speed | Fast | Fast | Depends |
| Privacy | Cloud | Cloud | Full |
| Cost | Pay-per-use | Pay-per-use | Free |
| Offline | No | No | Yes |
