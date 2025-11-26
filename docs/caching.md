# Caching

Fundas caches API responses to reduce redundant API calls and costs. This document explains how caching works and how to manage it.

## How Caching Works

When you make a request, Fundas generates a cache key based on:
- Content being analyzed
- Prompt used
- Model used
- Columns specified

If the same combination is requested again within the TTL (time-to-live), the cached response is returned instead of making a new API call.

## Cache Location

By default, cache files are stored in:
```
~/.fundas/cache/
```

Each cache entry is a JSON file named with its SHA256 hash key.

## Default Behavior

- **Enabled**: Caching is enabled by default
- **TTL**: 24 hours (86400 seconds)
- **Scope**: Per content/prompt/model combination

## Disabling Cache

### Per-Client

```python
from fundas import OpenRouterClient

client = OpenRouterClient(
    api_key="your-key",
    use_cache=False
)
```

### Globally

```python
from fundas.cache import get_cache

cache = get_cache()
cache.disable()
```

## Re-enabling Cache

```python
from fundas.cache import get_cache

cache = get_cache()
cache.enable()
```

## Custom TTL

Set a custom cache time-to-live:

```python
from fundas import OpenRouterClient

# Cache for 1 hour
client = OpenRouterClient(
    api_key="your-key",
    cache_ttl=3600
)
```

Or when getting the cache instance:

```python
from fundas.cache import get_cache

cache = get_cache(ttl=3600)  # 1 hour TTL
```

## Clearing Cache

### Clear All Entries

```python
from fundas.cache import get_cache

cache = get_cache()
count = cache.clear()
print(f"Cleared {count} entries")
```

### Clear Expired Entries

```python
from fundas.cache import get_cache

cache = get_cache()
count = cache.clear_expired()
print(f"Cleared {count} expired entries")
```

## Custom Cache Directory

```python
from fundas.cache import APICache

cache = APICache(
    cache_dir="/path/to/cache",
    ttl=86400
)
```

## Cache Key Generation

Cache keys are generated using SHA256 hash of:

```python
{
    "content": "...",
    "prompt": "...",
    "model": "...",
    "columns": [...]
}
```

This means different prompts on the same content will be cached separately.

## APICache Class

The `APICache` class provides full control over caching:

```python
from fundas.cache import APICache

cache = APICache(
    cache_dir="~/.fundas/cache",
    ttl=86400
)

# Check if data is cached
data = cache.get(content, prompt, model, columns)

# Cache new data
cache.set(content, prompt, model, data, columns)

# Manage cache
cache.enable()
cache.disable()
cache.clear()
cache.clear_expired()
```

## Cache File Format

Each cache entry is stored as JSON:

```json
{
    "timestamp": 1700000000.0,
    "data": {
        "column1": ["value1", "value2"],
        "column2": ["value3", "value4"]
    }
}
```

## Best Practices

1. **Keep cache enabled** for development to avoid unnecessary API calls
2. **Clear cache** when testing different prompts or models
3. **Use shorter TTL** for frequently changing content
4. **Disable cache** when you need fresh results every time
5. **Clear expired entries** periodically to save disk space

## Troubleshooting

### Cache Not Working

1. Check if cache is enabled: `cache.enabled`
2. Verify cache directory exists and is writable
3. Ensure content/prompt/model are identical

### Stale Data

Clear the cache to get fresh results:

```python
from fundas.cache import get_cache
get_cache().clear()
```

### Disk Space

Clear expired entries regularly:

```python
from fundas.cache import get_cache
get_cache().clear_expired()
```
