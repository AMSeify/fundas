# Webpage Reader

The `read_webpage()` function extracts structured data from web pages with extensive HTTP configuration options.

## Basic Usage

```python
import fundas as fd

df = fd.read_webpage(
    "https://example.com/products",
    prompt="Extract product names and prices"
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | str | Required | URL of the webpage |
| `prompt` | str | "Extract main content..." | Instructions for extraction |
| `columns` | list | None | Column names to extract |
| `schema` | Schema | None | Schema for typed output |
| `api_key` | str | None | OpenRouter API key |
| `model` | str | None | AI model |
| `headers` | dict | None | Custom HTTP headers |
| `cookies` | dict | None | Cookies to send |
| `proxy` | str | None | Proxy URL |
| `payload` | dict | None | POST/PUT request body |
| `method` | str | "GET" | HTTP method |
| `timeout` | int | 30 | Request timeout (seconds) |
| `verify_ssl` | bool | True | Verify SSL certificates |
| `follow_redirects` | bool | True | Follow HTTP redirects |
| `max_redirects` | int | 10 | Maximum redirects |
| `encoding` | str | None | Force response encoding |
| `auth` | tuple | None | (username, password) |
| `retry_count` | int | 3 | Number of retries |
| `retry_delay` | float | 1.0 | Delay between retries |

## Examples

### Extract Product Listings

```python
df = fd.read_webpage(
    "https://shop.example.com/products",
    prompt="Extract product names, prices, and ratings",
    columns=["name", "price", "rating"]
)
```

### With Authentication

```python
df = fd.read_webpage(
    "https://api.example.com/data",
    headers={"Authorization": "Bearer token123"},
)
```

### Using Basic Auth

```python
df = fd.read_webpage(
    "https://secure.example.com/report",
    auth=("username", "password"),
)
```

### POST Request

```python
df = fd.read_webpage(
    "https://api.example.com/search",
    method="POST",
    payload={"query": "python", "limit": 10},
)
```

### With Cookies

```python
df = fd.read_webpage(
    "https://dashboard.example.com",
    cookies={"session": "abc123", "user": "john"},
)
```

### Through Proxy

```python
df = fd.read_webpage(
    "https://example.com",
    proxy="http://proxy.company.com:8080",
)

# With authentication
df = fd.read_webpage(
    "https://example.com",
    proxy="http://user:pass@proxy.company.com:8080",
)

# SOCKS proxy
df = fd.read_webpage(
    "https://example.com",
    proxy="socks5://proxy.company.com:1080",
)
```

### Custom Headers

```python
df = fd.read_webpage(
    "https://api.example.com",
    headers={
        "Authorization": "Bearer token",
        "X-Custom-Header": "value",
        "User-Agent": "CustomBot/1.0",
    },
)
```

### Handling SSL Issues

```python
# Disable SSL verification (not recommended for production)
df = fd.read_webpage(
    "https://self-signed.example.com",
    verify_ssl=False,
)
```

### Force Encoding

```python
df = fd.read_webpage(
    "https://foreign-site.com",
    encoding="utf-8",
)
```

### Retry Configuration

```python
df = fd.read_webpage(
    "https://flaky-api.example.com",
    retry_count=5,
    retry_delay=2.0,  # 2 seconds base delay
)
```

## How It Works

1. Fetches the webpage with configured HTTP options
2. Parses HTML and removes scripts, styles, hidden elements
3. Extracts visible text content
4. Sends text to AI model for structured extraction

## Default Behavior

- Random user agent from common browsers
- Follows redirects (up to 10)
- Retries failed requests (3 times)
- Verifies SSL certificates
- 30 second timeout

## Tips

- Use custom headers to avoid being blocked
- Use proxies for geo-restricted content
- Increase timeout for slow sites
- Use `verify_ssl=False` only for testing

## Dependencies

- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing

```bash
pip install requests beautifulsoup4
```

## Error Handling

```python
try:
    df = fd.read_webpage("https://example.com")
except RuntimeError as e:
    if "403" in str(e):
        print("Access denied - try different headers")
    elif "404" in str(e):
        print("Page not found")
    elif "SSL" in str(e):
        print("SSL error - try verify_ssl=False")
    else:
        print(f"Error: {e}")
```
