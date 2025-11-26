"""
Webpage reader for Fundas.

This module provides the read_webpage function for extracting data from web pages.
"""

import pandas as pd
from typing import Optional, List, TYPE_CHECKING
import time
import random

from .base import _get_client, _extract_data, _apply_schema_dtypes

if TYPE_CHECKING:
    from ..schema import Schema


def read_webpage(
    url: str,
    prompt: str = "Extract main content and data from this webpage",
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    headers: Optional[dict] = None,
    cookies: Optional[dict] = None,
    proxy: Optional[str] = None,
    payload: Optional[dict] = None,
    method: str = "GET",
    timeout: int = 30,
    verify_ssl: bool = True,
    follow_redirects: bool = True,
    max_redirects: int = 10,
    encoding: Optional[str] = None,
    auth: Optional[tuple] = None,
    retry_count: int = 3,
    retry_delay: float = 1.0,
) -> pd.DataFrame:
    """
    Read a webpage and convert it to a pandas DataFrame using AI extraction.

    Args:
        url: URL of the webpage to read
        prompt: Prompt describing what data to extract from the webpage
        columns: Optional list of column names to extract
        schema: Optional Schema object for structured output with type enforcement
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)
        headers: Optional custom headers dict to override defaults
        cookies: Optional cookies dict to send with the request
        proxy: Optional proxy URL (e.g., "http://user:pass@proxy.com:8080"
            or "socks5://proxy.com:1080")
        payload: Optional payload for POST/PUT requests (dict or form data)
        method: HTTP method - "GET", "POST", "PUT", etc. (default: "GET")
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Whether to verify SSL certificates (default: True)
        follow_redirects: Whether to follow redirects (default: True)
        max_redirects: Maximum number of redirects to follow (default: 10)
        encoding: Force specific encoding for response (e.g., "utf-8")
        auth: Optional tuple of (username, password) for HTTP Basic Auth
        retry_count: Number of retries on failure (default: 3)
        retry_delay: Delay between retries in seconds (default: 1.0)

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> df = read_webpage("https://example.com/products", prompt="Extract products")
        >>> df = read_webpage("https://news.com/article", columns=["title", "author"])
        >>> df = read_webpage(
        ...     "https://api.example.com/data",
        ...     headers={"Authorization": "Bearer token123"},
        ...     proxy="http://proxy.com:8080"
        ... )
        >>> df = read_webpage(
        ...     "https://example.com/login",
        ...     method="POST",
        ...     payload={"username": "user", "password": "pass"},
        ...     cookies={"session": "abc123"}
        ... )
    """
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "requests and beautifulsoup4 are required. "
            "Install with: pip install requests beautifulsoup4"
        )

    # Default headers that mimic a real browser
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
        "Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    ]
    default_headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "DNT": "1",
    }

    # Merge custom headers with defaults (custom takes precedence)
    if headers:
        default_headers.update(headers)
    request_headers = default_headers

    # Set up proxy configuration
    proxies = None
    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy,
        }

    # Create session with retry logic
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=retry_count,
        backoff_factor=retry_delay,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Configure session
    session.max_redirects = max_redirects
    if not follow_redirects:
        session.max_redirects = 0

    # Fetch webpage content
    last_error = None
    for attempt in range(retry_count):
        try:
            # Prepare request kwargs
            request_kwargs = {
                "headers": request_headers,
                "timeout": timeout,
                "verify": verify_ssl,
                "allow_redirects": follow_redirects,
            }

            if proxies:
                request_kwargs["proxies"] = proxies

            if cookies:
                request_kwargs["cookies"] = cookies

            if auth:
                request_kwargs["auth"] = auth

            # Make request based on method
            method_upper = method.upper()
            if method_upper == "GET":
                response = session.get(url, **request_kwargs)
            elif method_upper == "POST":
                if payload:
                    # Check if payload should be JSON or form data
                    if isinstance(payload, dict):
                        request_kwargs["json"] = payload
                    else:
                        request_kwargs["data"] = payload
                response = session.post(url, **request_kwargs)
            elif method_upper == "PUT":
                if payload:
                    request_kwargs["json"] = payload
                response = session.put(url, **request_kwargs)
            elif method_upper == "DELETE":
                response = session.delete(url, **request_kwargs)
            elif method_upper == "HEAD":
                response = session.head(url, **request_kwargs)
            elif method_upper == "OPTIONS":
                response = session.options(url, **request_kwargs)
            elif method_upper == "PATCH":
                if payload:
                    request_kwargs["json"] = payload
                response = session.patch(url, **request_kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # Force encoding if specified
            if encoding:
                response.encoding = encoding

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "noscript", "iframe", "svg"]):
                element.decompose()

            # Remove hidden elements
            for element in soup.find_all(
                style=lambda x: x and "display:none" in x.replace(" ", "")
            ):
                element.decompose()
            for element in soup.find_all(
                style=lambda x: x and "visibility:hidden" in x.replace(" ", "")
            ):
                element.decompose()

            # Get text content
            text = soup.get_text(separator="\n")

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = "\n".join(chunk for chunk in chunks if chunk)

            # Add metadata to content
            content = f"URL: {url}\nStatus Code: {response.status_code}\n\n{content}"

            # Success - break out of retry loop
            break

        except requests.exceptions.SSLError as e:
            last_error = f"SSL Error: {str(e)}. Try setting verify_ssl=False"
            if attempt < retry_count - 1:
                time.sleep(retry_delay * (attempt + 1))
            continue

        except requests.exceptions.ProxyError as e:
            last_error = f"Proxy Error: {str(e)}. Check your proxy configuration"
            if attempt < retry_count - 1:
                time.sleep(retry_delay * (attempt + 1))
            continue

        except requests.exceptions.Timeout as e:
            last_error = f"Timeout Error: {str(e)}. Try increasing timeout value"
            if attempt < retry_count - 1:
                time.sleep(retry_delay * (attempt + 1))
            continue

        except requests.exceptions.TooManyRedirects as e:
            last_error = (
                f"Too many redirects: {str(e)}. "
                "Try setting follow_redirects=False or increasing max_redirects"
            )
            break  # Don't retry on redirect loops

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            if status_code == 403:
                last_error = (
                    "403 Forbidden: Access denied. "
                    "Try using different headers, cookies, or a proxy"
                )
            elif status_code == 401:
                last_error = (
                    "401 Unauthorized: Authentication required. " "Use auth parameter"
                )
            elif status_code == 404:
                last_error = "404 Not Found: The requested URL does not exist"
                break  # Don't retry on 404
            elif status_code == 429:
                last_error = (
                    "429 Too Many Requests: Rate limited. "
                    "Try using a proxy or increasing retry_delay"
                )
            else:
                last_error = f"HTTP Error {status_code}: {str(e)}"
            if attempt < retry_count - 1:
                time.sleep(
                    retry_delay * (attempt + 1) * 2
                )  # Longer delay for HTTP errors
            continue

        except Exception as e:
            last_error = f"Error fetching webpage: {str(e)}"
            if attempt < retry_count - 1:
                time.sleep(retry_delay * (attempt + 1))
            continue

    else:
        # All retries failed
        raise RuntimeError(last_error)

    # Use OpenRouter to extract structured data
    client = _get_client(api_key, model)
    data = _extract_data(client, content, prompt, columns, schema)

    df = pd.DataFrame(data)
    return _apply_schema_dtypes(df, schema)
