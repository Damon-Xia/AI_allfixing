# Configuration Guide

AI AllFixing supports flexible configuration through YAML files, environment variables, and CLI flags.

## Configuration File

The default config file is located at `~/.ai-allfixing/config.yaml`.

### Full Example

```yaml
provider:
  name: openai
  api_key: sk-your-key-here
  model: gpt-4o
  base_url: null
  max_tokens: 4096
  temperature: 0.1
  extra: {}

log_level: INFO
cache_enabled: true
cache_dir: ~/.ai-allfixing/cache
output_format: text
```

## Provider Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `name` | Provider name (openai, anthropic) | openai |
| `api_key` | API key for the provider | (from env) |
| `model` | Model to use | gpt-4o |
| `base_url` | Custom API endpoint (for Azure/local) | null |
| `max_tokens` | Max response tokens | 4096 |
| `temperature` | Sampling temperature (0.0-2.0) | 0.1 |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key |

## CLI Overrides

Any command supports provider/model override:

```bash
# Use a specific provider for one command
ai-fix --provider anthropic --model claude-sonnet-4-20250514 code fix file.py

# Verbose mode for debugging
ai-fix -v code review app.py
```

## Managing Config via CLI

```bash
# Show current config
ai-fix config show

# Set a value
ai-fix config set provider.model gpt-4
ai-fix config set provider.name anthropic
ai-fix config set log_level DEBUG

# Get a value
ai-fix config get provider.model
```

## Caching

Responses are cached by default to reduce API costs during development:

```yaml
cache_enabled: true
cache_dir: ~/.ai-allfixing/cache
```

Disable caching:

```bash
ai-fix config set cache_enabled false
```

## Multiple Profiles

You can maintain multiple config files for different scenarios:

```bash
# Use a specific config file
AI_ALLFIXING_CONFIG=~/.ai-allfixing/work.yaml ai-fix code fix file.py
```
