"""
Fundas - AI-powered data import library

Fundas extends pandas to import and analyze complex, unstructured files
using generative AI via the OpenRouter API.

Main functions:
    - read_pdf: Extract structured data from PDF files
    - read_image: Extract structured data from images
    - read_audio: Extract structured data from audio files
    - read_webpage: Extract structured data from web pages
    - read_video: Extract structured data from videos
"""

__version__ = "0.1.0"

from .readers import (
    read_pdf,
    read_image,
    read_audio,
    read_webpage,
    read_video,
)

from .core import OpenRouterClient

__all__ = [
    "read_pdf",
    "read_image",
    "read_audio",
    "read_webpage",
    "read_video",
    "OpenRouterClient",
]
