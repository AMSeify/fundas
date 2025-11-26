"""
PDF reader for Fundas.

This module provides the read_pdf function for extracting data from PDF files.
"""

import pandas as pd
from typing import Optional, List, Union, TYPE_CHECKING
from pathlib import Path

from .base import _get_client, _extract_data, _apply_schema_dtypes

if TYPE_CHECKING:
    from ..schema import Schema


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
            enforcement. When provided, the output will have proper
            data types (int, float, date, etc.)
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> df = read_pdf("invoice.pdf", prompt="Extract invoice items")
        >>> df = read_pdf("report.pdf", columns=["date", "metric", "value"])
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
