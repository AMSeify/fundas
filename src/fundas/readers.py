"""
Fundas - AI-powered file import functions

This module provides backward compatibility with the old readers.py location.
The readers have been moved to the fundas.readers package.
"""

# Re-export all readers from new location for backward compatibility
from .readers import (
    read_pdf,
    read_image,
    read_audio,
    read_webpage,
    read_video,
    _get_client,
    _extract_data,
    _apply_schema_dtypes,
)

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
