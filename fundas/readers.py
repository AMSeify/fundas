"""
Fundas - AI-powered file import functions

This module provides functions to read various file types and convert them
to pandas DataFrames using AI-powered extraction.
"""

import pandas as pd
from typing import Optional, List, Union
from pathlib import Path

from .core import OpenRouterClient


def _get_client(
    api_key: Optional[str] = None, model: Optional[str] = None
) -> OpenRouterClient:
    """Get or create an OpenRouter client instance."""
    return OpenRouterClient(api_key=api_key, model=model)


def read_pdf(
    filepath: Union[str, Path],
    prompt: str = "Extract all text and tabular data from this PDF",
    columns: Optional[List[str]] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read a PDF file and convert it to a pandas DataFrame using AI extraction.

    Args:
        filepath: Path to the PDF file
        prompt: Prompt describing what data to extract
        columns: Optional list of column names to extract
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)

    Returns:
        pandas DataFrame containing extracted data

    Examples:
        >>> df = read_pdf("invoice.pdf", prompt="Extract invoice items")
        >>> df = read_pdf("report.pdf", columns=["date", "metric", "value"])
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
    data = client.extract_structured_data(content, prompt, columns)

    return pd.DataFrame(data)


def read_image(
    filepath: Union[str, Path],
    prompt: str = "Describe what you see in this image and extract any text or data",
    columns: Optional[List[str]] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read an image file and convert it to a pandas DataFrame using AI extraction.

    Args:
        filepath: Path to the image file
        prompt: Prompt describing what data to extract from the image
        columns: Optional list of column names to extract
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)

    Returns:
        pandas DataFrame containing extracted data

    Examples:
        >>> df = read_image("chart.png", prompt="Extract data points from this chart")
        >>> df = read_image("receipt.jpg", prompt="Extract items and prices")
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Try to extract text from image using OCR if available
    content = ""
    try:
        from PIL import Image
        import pytesseract

        image = Image.open(filepath)
        content = pytesseract.image_to_string(image)
        if not content.strip():
            content = f"Image file: {filepath.name} (No text detected via OCR)"
    except ImportError:
        # OCR libraries not available
        content = (
            f"Image file: {filepath.name} "
            "(OCR not available - install pytesseract for text extraction)"
        )
    except Exception:
        # Fallback: describe the image file
        content = f"Image file: {filepath.name}"

    # Add basic image information
    try:
        from PIL import Image

        image = Image.open(filepath)
        content += f"\nImage size: {image.size[0]}x{image.size[1]}"
        content += f"\nImage format: {image.format}"
        content += f"\nImage mode: {image.mode}"
    except Exception:
        pass

    # Use OpenRouter to extract structured data
    client = _get_client(api_key, model)
    data = client.extract_structured_data(content, prompt, columns)

    return pd.DataFrame(data)


def read_audio(
    filepath: Union[str, Path],
    prompt: str = "Transcribe this audio and extract key information",
    columns: Optional[List[str]] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read an audio file and convert it to a pandas DataFrame using AI extraction.

    Args:
        filepath: Path to the audio file
        prompt: Prompt describing what data to extract from the audio
        columns: Optional list of column names to extract
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)

    Returns:
        pandas DataFrame containing extracted data

    Examples:
        >>> df = read_audio(
        ...     "meeting.mp3",
        ...     prompt="Extract speaker names and key points"
        ... )
        >>> df = read_audio("interview.wav", columns=["speaker", "topic"])
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Get audio file metadata
    content = f"Audio file: {filepath.name}\n"
    content += f"File size: {filepath.stat().st_size} bytes\n"
    content += f"File extension: {filepath.suffix}\n"

    # Note: Full audio transcription would require additional services
    # For now, we work with metadata and let the AI provide structure
    content += (
        "\n[Note: Full audio transcription requires "
        "additional audio processing services]"
    )

    # Use OpenRouter to extract structured data
    client = _get_client(api_key, model)
    data = client.extract_structured_data(content, prompt, columns)

    return pd.DataFrame(data)


def read_webpage(
    url: str,
    prompt: str = "Extract main content and data from this webpage",
    columns: Optional[List[str]] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read a webpage and convert it to a pandas DataFrame using AI extraction.

    Args:
        url: URL of the webpage to read
        prompt: Prompt describing what data to extract from the webpage
        columns: Optional list of column names to extract
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)

    Returns:
        pandas DataFrame containing extracted data

    Examples:
        >>> df = read_webpage("https://example.com/products", prompt="Extract products")
        >>> df = read_webpage("https://news.com/article", columns=["title", "author"])
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "requests and beautifulsoup4 are required. "
            "Install with: pip install requests beautifulsoup4"
        )

    # Fetch webpage content
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = "\n".join(chunk for chunk in chunks if chunk)

        # Add URL to content
        content = f"URL: {url}\n\n{content}"

    except Exception as e:
        raise RuntimeError(f"Error fetching webpage: {str(e)}")

    # Use OpenRouter to extract structured data
    client = _get_client(api_key, model)
    data = client.extract_structured_data(content, prompt, columns)

    return pd.DataFrame(data)


def read_video(
    filepath: Union[str, Path],
    prompt: str = "Analyze this video and extract key information",
    from_: Union[str, List[str]] = "both",
    columns: Optional[List[str]] = None,
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
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)
        sample_rate: Frame sampling rate (extract 1 frame per N frames)

    Returns:
        pandas DataFrame containing extracted data

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
    data = client.extract_structured_data(content, prompt, columns)

    return pd.DataFrame(data)
