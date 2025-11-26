"""
Image reader for Fundas.

This module provides the read_image function for extracting data from images.
"""

import pandas as pd
from typing import Optional, List, Union, TYPE_CHECKING
from pathlib import Path

from .base import _get_client, _extract_data, _apply_schema_dtypes

if TYPE_CHECKING:
    from ..schema import Schema


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
        >>> df = read_image("chart.png", prompt="Extract data points from this chart")
        >>> df = read_image(
        ...     "receipt.jpg", prompt="Extract items and prices", mode="ocr"
        ... )
        >>> df = read_image("arabic.png", mode="ocr", language="ara")

        >>> # Direct mode - send image directly to vision model
        >>> df = read_image("photo.jpg", mode="direct",
        ...                 model="openai/gpt-5-mini",
        ...                 prompt="Describe the scene")

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
                    f"(No text detected via OCR with language={language})"
                )
        except ImportError:
            # OCR libraries not available
            content = (
                f"Image file: {filepath.name} "
                "(OCR not available - install pytesseract for text extraction)"
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
