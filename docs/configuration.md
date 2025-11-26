# Configuration

Fundas can be configured through environment variables, function parameters, or a `.env` file.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `OPENROUTER_MODEL` | Default AI model to use | `openai/gpt-3.5-turbo` |

## Setting the API Key

### Environment Variable

```bash
export OPENROUTER_API_KEY="your-api-key"
```

### In Python

```python
import os
os.environ["OPENROUTER_API_KEY"] = "your-api-key"
```

### Per-Function

```python
df = fd.read_pdf("file.pdf", api_key="your-api-key")
```

### Using .env File

Create a `.env` file in your project root:

```
OPENROUTER_API_KEY=your-api-key
OPENROUTER_MODEL=openai/gpt-4
```

Fundas automatically loads `.env` files using `python-dotenv`.

## Model Selection

### Default Model

The default model is `openai/gpt-3.5-turbo`. Change it via environment variable:

```bash
export OPENROUTER_MODEL="anthropic/claude-3-opus"
```

### Per-Function Model

Override the model for specific calls:

```python
df = fd.read_pdf("file.pdf", model="anthropic/claude-3-opus")
```

### Recommended Models

| Use Case | Recommended Model |
|----------|------------------|
| General text extraction | `openai/gpt-3.5-turbo` |
| Complex documents | `anthropic/claude-3-opus` |
| Vision (direct image) | `openai/gpt-4-vision-preview` |
| Audio (OpenRouter) | `google/gemini-2.5-flash` |

## Cache Configuration

Fundas caches API responses to avoid redundant calls. Configure via `OpenRouterClient`:

```python
from fundas import OpenRouterClient

client = OpenRouterClient(
    api_key="your-key",
    use_cache=True,       # Enable caching (default: True)
    cache_ttl=86400,      # Cache TTL in seconds (default: 24 hours)
)
```

### Cache Directory

Cache files are stored in `~/.fundas/cache/` by default.

### Disabling Cache

```python
from fundas.cache import get_cache

cache = get_cache()
cache.disable()  # Disable caching
cache.enable()   # Re-enable caching
cache.clear()    # Clear all cached data
```

## Retry Configuration

API calls are automatically retried on failure:

```python
from fundas import OpenRouterClient

client = OpenRouterClient(
    api_key="your-key",
    max_retries=3,    # Number of retry attempts (default: 3)
    retry_delay=1,    # Base delay between retries in seconds (default: 1)
)
```

The retry uses exponential backoff: delay × (attempt + 1).

## Web Scraping Configuration

`read_webpage()` supports extensive HTTP configuration:

```python
df = fd.read_webpage(
    "https://example.com",
    headers={"Authorization": "Bearer token"},
    cookies={"session": "abc123"},
    proxy="http://proxy.com:8080",
    timeout=30,
    verify_ssl=True,
    follow_redirects=True,
    max_redirects=10,
    retry_count=3,
    retry_delay=1.0,
)
```

## Audio Configuration

`read_audio()` supports local Whisper or OpenRouter:

```python
# Local Whisper (default)
df = fd.read_audio(
    "audio.mp3",
    whisper_model="base",  # tiny, base, small, medium, large
    device="cpu",          # cpu or cuda
    language="en",         # ISO language code
)

# OpenRouter (better for non-English)
df = fd.read_audio(
    "audio.mp3",
    use_openrouter=True,
    model="google/gemini-2.5-flash",
    language="Persian",
)
```

## Image Configuration

`read_image()` supports OCR or direct vision:

```python
# OCR mode (default)
df = fd.read_image(
    "image.png",
    mode="ocr",
    language="eng",  # tesseract language code
)

# Direct vision mode
df = fd.read_image(
    "image.png",
    mode="direct",
    model="openai/gpt-4-vision-preview",
)
```
