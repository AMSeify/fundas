"""
Fundas - AI-powered file import functions

This module provides functions to read various file types and convert them
to pandas DataFrames using AI-powered extraction.
"""

import pandas as pd
from typing import Optional, List, Union, TYPE_CHECKING
from pathlib import Path

from .core import OpenRouterClient

if TYPE_CHECKING:
    from fundas.schema import Schema


def _get_client(
    api_key: Optional[str] = None, model: Optional[str] = None
) -> OpenRouterClient:
    """Get or create an OpenRouter client instance."""
    return OpenRouterClient(api_key=api_key, model=model)


def _extract_data(
    client: OpenRouterClient,
    content: str,
    prompt: str,
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
) -> dict:
    """
    Extract data using either schema-based or column-based extraction.

    Args:
        client: OpenRouter client instance
        content: Content to analyze
        prompt: Extraction prompt
        columns: Optional column names (used if schema is None)
        schema: Optional Schema object for structured output with types

    Returns:
        Dictionary of extracted data
    """
    if schema is not None:
        return client.extract_structured_data_with_schema(content, prompt, schema)
    else:
        return client.extract_structured_data(content, prompt, columns)


def _apply_schema_dtypes(df: pd.DataFrame, schema: Optional["Schema"]) -> pd.DataFrame:
    """
    Apply schema data types to DataFrame columns.

    Args:
        df: DataFrame to convert
        schema: Schema with column type definitions

    Returns:
        DataFrame with converted types
    """
    if schema is None:
        return df

    for col in schema.columns:
        if col.name in df.columns:
            # The conversion is already done in extract_structured_data_with_schema
            # But we can apply pandas-specific optimizations here
            from .schema import DataType

            if col.dtype == DataType.INTEGER:
                # Use nullable integer type
                df[col.name] = pd.to_numeric(df[col.name], errors="coerce").astype(
                    "Int64"
                )
            elif col.dtype == DataType.FLOAT:
                df[col.name] = pd.to_numeric(df[col.name], errors="coerce")
            elif col.dtype == DataType.BOOLEAN:
                df[col.name] = df[col.name].astype(bool)
            elif col.dtype == DataType.DATE:
                df[col.name] = pd.to_datetime(df[col.name], errors="coerce").dt.date
            elif col.dtype == DataType.DATETIME:
                df[col.name] = pd.to_datetime(df[col.name], errors="coerce")

    return df


def read_pdf(
    filepath: Union[str, Path],
    prompt: str = "Extract all text and tabular data from this PDF",
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read a PDF file and convert it to a pandas DataFrame using AI extraction.

    Args:
        filepath: Path to the PDF file
        prompt: Prompt describing what data to extract
        columns: Optional list of column names to extract
        schema: Optional Schema object for structured output with type
            enforcement. When provided, the output will have proper data
            types (int, float, date, etc.)
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> df = read_pdf("invoice.pdf", prompt="Extract invoice items")
        >>> df = read_pdf(
        ...     "report.pdf", columns=["date", "metric", "value"]
        ... )
        >>> # With schema for typed output
        >>> from fundas.schema import Schema, Column, DataType
        >>> schema = Schema([
        ...     Column("item", DataType.STRING),
        ...     Column("price", DataType.FLOAT),
        ...     Column("quantity", DataType.INTEGER),
        ... ])
        >>> df = read_pdf("invoice.pdf", prompt="Extract items", schema=schema)
    """
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError(
            "PyPDF2 is required for read_pdf. Install it with: pip install PyPDF2"
        )

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Extract text from PDF
    try:
        reader = PdfReader(str(filepath))
        text_content = []
        for page in reader.pages:
            text_content.append(page.extract_text())
        content = "\n\n--- Page Break ---\n\n".join(text_content)
    except Exception as e:
        raise RuntimeError(f"Error reading PDF file: {str(e)}")

    # Use OpenRouter to extract structured data
    client = _get_client(api_key, model)
    data = _extract_data(client, content, prompt, columns, schema)

    df = pd.DataFrame(data)
    return _apply_schema_dtypes(df, schema)


def read_image(
    filepath: Union[str, Path],
    prompt: str = "Describe what you see in this image and extract any text or data",
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    mode: str = "ocr",
    language: str = "eng",
) -> pd.DataFrame:
    """
    Read an image file and convert it to a pandas DataFrame using AI extraction.

    Args:
        filepath: Path to the image file
        prompt: Prompt describing what data to extract from the image
        columns: Optional list of column names to extract
        schema: Optional Schema object for structured output with type enforcement
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo for OCR mode,
            gpt-5-mini recommended for direct mode)
        mode: Extraction mode - "ocr" (extract text via OCR then send to LLM) or
            "direct" (send image directly to vision-capable LLM)
        language: Language code for OCR (default: "eng").
            Examples: "eng", "ara", "fas", "spa".
            Only used when mode="ocr".
            See pytesseract documentation for full list.

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> # OCR mode (default) - extract text from image first
        >>> df = read_image(
        ...     "chart.png", prompt="Extract data points from this chart"
        ... )
        >>> df = read_image(
        ...     "receipt.jpg",
        ...     prompt="Extract items and prices",
        ...     mode="ocr",
        ... )
        >>> df = read_image("arabic.png", mode="ocr", language="ara")

        >>> # Direct mode - send image directly to vision model
        >>> df = read_image(
        ...     "photo.jpg",
        ...     mode="direct",
        ...     model="openai/gpt-5-mini",
        ...     prompt="Describe the scene",
        ... )

        >>> # With schema for typed output
        >>> from fundas.schema import Schema, Column, DataType
        >>> schema = Schema([
        ...     Column("item", DataType.STRING),
        ...     Column("price", DataType.FLOAT),
        ... ])
        >>> df = read_image("receipt.jpg", prompt="Extract items", schema=schema)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Validate mode
    if mode not in ["ocr", "direct"]:
        raise ValueError(f"Invalid mode: {mode}. Must be 'ocr' or 'direct'")

    client = _get_client(api_key, model)

    if mode == "direct":
        # Direct mode: encode image as base64 and send to vision model
        try:
            import base64
            from PIL import Image

            # Read and encode image
            with open(filepath, "rb") as image_file:
                image_data = image_file.read()

            # Get image format
            image = Image.open(filepath)
            image_format = image.format.lower() if image.format else "png"

            # Create data URI
            base64_image = base64.b64encode(image_data).decode("utf-8")
            image_uri = f"data:image/{image_format};base64,{base64_image}"

            # Use vision-capable extraction
            # Note: Vision mode doesn't support schema yet
            cols = schema.get_column_names() if schema else columns
            data = client.extract_structured_data_from_image(image_uri, prompt, cols)

        except ImportError:
            raise ImportError(
                "PIL is required for direct mode. Install it with: pip install Pillow"
            )
        except Exception as e:
            raise RuntimeError(f"Error processing image in direct mode: {str(e)}")

    else:  # mode == "ocr"
        # OCR mode: extract text from image using OCR, then send text to LLM
        content = ""
        try:
            from PIL import Image
            import pytesseract

            image = Image.open(filepath)
            # Use language parameter for OCR
            content = pytesseract.image_to_string(image, lang=language)
            if not content.strip():
                content = (
                    f"Image file: {filepath.name} "
                    f"(No text detected via OCR with language={language})",
                )
        except ImportError:
            # OCR libraries not available
            content = (
                f"Image file: {filepath.name} "
                "(OCR not available - install pytesseract for text "
                "extraction)"
            )
        except Exception as e:
            # Fallback: describe the image file
            content = f"Image file: {filepath.name} (OCR error: {str(e)})"

        # Add basic image information
        try:
            from PIL import Image

            image = Image.open(filepath)
            content += f"\nImage size: {image.size[0]}x{image.size[1]}"
            content += f"\nImage format: {image.format}"
            content += f"\nImage mode: {image.mode}"
        except Exception:
            pass

        # Use text-based extraction with schema support
        data = _extract_data(client, content, prompt, columns, schema)

    df = pd.DataFrame(data)
    return _apply_schema_dtypes(df, schema)


def read_audio(
    filepath: Union[str, Path],
    prompt: str = "Transcribe this audio and extract key information",
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    language: Optional[str] = None,
    whisper_model: str = "base",
    device: Optional[str] = None,
    use_openrouter: bool = False,
) -> pd.DataFrame:
    """
    Read an audio file and convert it to a pandas DataFrame using AI extraction.

    This function supports two transcription methods:

    1.  **Local Whisper (default)**: Uses OpenAI's Whisper model locally
        for transcription, then sends text to an LLM for structured
        extraction.
    2.  **OpenRouter API (`use_openrouter=True`)**: Sends audio directly
        to audio-capable models like ``google/gemini-2.5-flash`` for
        transcription and extraction in one step.

    Supports MP3 and WAV formats for OpenRouter, and additional formats (FLAC,
    OGG, M4A, etc.) for local Whisper transcription.

    Args:
        filepath: Path to the audio file.
        prompt: Prompt describing what data to extract from the audio.
        columns: Optional list of column names to extract.
        schema: Optional :class:`~fundas.schema.Schema` object for structured
            output with type enforcement.
        api_key: Optional OpenRouter API key.
        model: Optional AI model to use.
        language: Language specification for better accuracy.
        whisper_model: Whisper model size for local transcription (e.g.,
            "base", "medium", "large").
        device: Device to run local Whisper on ("cuda", "cpu").
        use_openrouter: If ``True``, sends audio directly to OpenRouter.
            This is recommended for non-English languages.
        device: Device to run local Whisper on ("cuda", "cpu", or None).
            Use "cpu" if you encounter GPU memory issues.
        use_openrouter: If True, send audio directly to OpenRouter.
            This is often more accurate for non-English languages.
            Default: False (use local Whisper)

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> # Basic transcription with local Whisper (English)
        >>> df = read_audio(
        ...     "meeting.mp3",
        ...     prompt="Extract speaker names and key points",
        ...     language="en"
        ... )

        >>> # Persian audio with local Whisper
        >>> df = read_audio(
        ...     "persian_audio.mp3",
        ...     prompt="Extract the artist name and song lyrics",
        ...     language="fa",  # Persian/Farsi code for Whisper
        ...     whisper_model="medium"  # Use larger model for non-English
        ... )

        >>> # Persian audio with OpenRouter (recommended for non-English)
        >>> df = read_audio(
        ...     "persian_song.mp3",
        ...     prompt="Extract each verse with artist name (Ebi, "
        ...     "Shadmehr, etc.)",
        ...     columns=["verse_number", "artist", "lyrics"],
        ...     language="Persian",  # Full language name for OpenRouter
        ...     use_openrouter=True,
        ...     model="google/gemini-2.5-flash",  # Audio-capable model
        ... )

        >>> # Extract song information into multiple rows
        >>> df = read_audio(
        ...     "music.mp3",
        ...     prompt="Extract each song/verse as a separate row with "
        ...     "artist name",
        ...     columns=["artist", "lyrics", "verse_number"],
        ...     language="Farsi",
        ...     use_openrouter=True,
        ...     model="google/gemini-2.5-flash",
        ... )
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Initialize client
    client = _get_client(api_key, model)

    if use_openrouter:
        # Send audio directly to OpenRouter audio-capable model
        # This method is better for non-English languages and complex extraction
        try:
            data = client.extract_structured_data_from_audio(
                str(filepath),
                prompt=prompt,
                columns=columns,
                language=language,
            )
            df = pd.DataFrame(data)
            return _apply_schema_dtypes(df, schema)

        except Exception as e:
            raise RuntimeError(
                f"Error processing audio with OpenRouter: {str(e)}. "
                "Make sure you're using an audio-capable model like "
                "'google/gemini-2.5-flash'. Check supported models at: "
                "https://openrouter.ai/models?input_modalities=audio"
            ) from e

    else:
        # Use local Whisper for transcription, then LLM for extraction
        # Get audio file metadata
        metadata = f"Audio file: {filepath.name}\n"
        metadata += f"File size: {filepath.stat().st_size} bytes\n"
        metadata += f"File extension: {filepath.suffix}\n"

        transcription = ""
        try:
            import whisper
            import torch

            # Determine device - prefer CUDA but fall back to CPU
            if device is None:
                compute_device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                compute_device = device
            use_fp16 = compute_device == "cuda"

            # Load the Whisper model
            whisper_mdl = whisper.load_model(whisper_model, device=compute_device)

            # Transcribe with language specification
            transcribe_options = {"fp16": use_fp16}
            if language:
                transcribe_options["language"] = language
                transcribe_options["task"] = "transcribe"

            try:
                result = whisper_mdl.transcribe(str(filepath), **transcribe_options)
                transcription = result.get("text", "")
            except RuntimeError as gpu_error:
                # If CUDA fails, retry on CPU
                if compute_device == "cuda":
                    whisper_mdl = whisper.load_model(whisper_model, device="cpu")
                    transcribe_options["fp16"] = False
                    result = whisper_mdl.transcribe(str(filepath), **transcribe_options)
                    transcription = result.get("text", "")
                else:
                    raise gpu_error

            # Add language info
            detected_lang = result.get("language", "unknown")
            if not language:
                metadata += f"Detected language: {detected_lang}\n"
            else:
                metadata += f"Specified language: {language}\n"
            metadata += f"Whisper model: {whisper_model}\n"

        except ImportError:
            transcription = (
                "[Whisper not installed. Install with: pip install "
                "openai-whisper]\n"
                "[Note: You may also need ffmpeg installed on your system]\n"
                "[Alternatively, use use_openrouter=True with an audio model]"
            )
        except Exception as e:
            transcription = f"[Transcription error: {str(e)}]"

        # Combine metadata and transcription
        content = metadata + "\n--- Transcription ---\n" + transcription

        # Use LLM to extract structured data from transcription
        data = _extract_data(client, content, prompt, columns, schema)

        df = pd.DataFrame(data)
        return _apply_schema_dtypes(df, schema)


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
        proxy: Optional proxy URL (e.g.,
            "http://user:pass@proxy.com:8080" or "socks5://proxy.com:1080")
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
        >>> df = read_webpage(
        ...     "https://example.com/products", prompt="Extract products"
        ... )
        >>> df = read_webpage(
        ...     "https://news.com/article", columns=["title", "author"]
        ... )
        >>> df = read_webpage(
        ...     "https://api.example.com/data",
        ...     headers={"Authorization": "Bearer token123"},
        ...     proxy="http://proxy.com:8080",
        ... )
        >>> df = read_webpage(
        ...     "https://example.com/login",
        ...     method="POST",
        ...     payload={"username": "user", "password": "pass"},
        ...     cookies={"session": "abc123"}
        ... )
    """
    import time
    import random

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
        allowed_methods=[
            "HEAD",
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
            "TRACE",
        ],
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
                "Try setting follow_redirects=False or increasing "
                "max_redirects"
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


def read_video(
    filepath: Union[str, Path],
    prompt: str = "Analyze this video and extract key information",
    from_: Union[str, List[str]] = "both",
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    sample_rate: int = 30,
) -> pd.DataFrame:
    """
    Read a video file and convert it to a pandas DataFrame using AI extraction.

    Args:
        filepath: Path to the video file
        prompt: Prompt describing what data to extract from the video
        from_: Source(s) to extract from -
            'pics' (frames), 'audios' (audio track), or 'both'
        columns: Optional list of column names to extract
        schema: Optional Schema object for structured output with type
            enforcement
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)
        sample_rate: Frame sampling rate (extract 1 frame per N frames)

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> df = read_video(
        ...     "presentation.mp4",
        ...     prompt="Extract slide titles",
        ...     from_="pics"
        ... )
        >>> df = read_video("lecture.mp4", from_="audios")
        >>> df = read_video("interview.mp4", from_="both")
    """
    try:
        import cv2
    except ImportError:
        raise ImportError(
            "opencv-python is required for read_video. "
            "Install it with: pip install opencv-python"
        )

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Normalize from_ parameter
    if isinstance(from_, str):
        from_ = [from_]

    valid_options = {"pics", "audios", "both"}
    for option in from_:
        if option not in valid_options:
            raise ValueError(
                f"Invalid 'from_' option: {option}. Must be one of {valid_options}"
            )

    if "both" in from_:
        from_ = ["pics", "audios"]

    content = f"Video file: {filepath.name}\n"
    content += f"File size: {filepath.stat().st_size} bytes\n"

    # Extract video information
    try:
        video = cv2.VideoCapture(str(filepath))
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        content += f"Duration: {duration:.2f} seconds\n"
        content += f"Frame rate: {fps:.2f} fps\n"
        content += f"Resolution: {width}x{height}\n"
        content += f"Total frames: {frame_count}\n"

        if "pics" in from_:
            content += "\n--- Frame Analysis ---\n"
            content += f"Sampling every {sample_rate} frames\n"

            # Sample frames from the video
            frame_descriptions = []
            frame_idx = 0
            while frame_idx < frame_count:
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = video.read()
                if not ret:
                    break

                # Basic frame description
                # (in a real implementation, use OCR or vision models)
                timestamp = frame_idx / fps if fps > 0 else 0
                frame_descriptions.append(f"Frame at {timestamp:.2f}s")

                frame_idx += sample_rate

            content += f"Sampled {len(frame_descriptions)} frames\n"
            content += "\n".join(
                frame_descriptions[:10]
            )  # Limit to first 10 for brevity
            if len(frame_descriptions) > 10:
                content += f"\n... and {len(frame_descriptions) - 10} more frames"

        if "audios" in from_:
            content += "\n\n--- Audio Analysis ---\n"
            content += (
                "[Note: Full audio extraction requires "
                "additional audio processing services]\n"
            )

        video.release()

    except Exception as e:
        content += f"\nError analyzing video: {str(e)}"

    # Use OpenRouter to extract structured data
    client = _get_client(api_key, model)
    data = _extract_data(client, content, prompt, columns, schema)

    df = pd.DataFrame(data)
    return _apply_schema_dtypes(df, schema)
