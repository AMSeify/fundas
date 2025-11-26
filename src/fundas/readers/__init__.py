"""
Fundas readers package.

This package provides functions to read various file types and convert them
to pandas DataFrames using AI-powered extraction.
"""

from .pdf import read_pdf
from .image import read_image
from .audio import read_audio
from .webpage import read_webpage
from .video import read_video
from .base import _get_client, _extract_data, _apply_schema_dtypes

__all__ = [
    "read_pdf",
    "read_image",
    "read_audio",
    "read_webpage",
    "read_video",
    "_get_client",
    "_extract_data",
    "_apply_schema_dtypes",
]
