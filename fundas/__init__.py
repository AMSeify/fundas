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
    - to_summarized_csv: Export DataFrame to CSV with AI summarization
    - to_summarized_excel: Export DataFrame to Excel with AI summarization
    - to_summarized_json: Export DataFrame to JSON with AI summarization
    - summarize_dataframe: Generate AI summary of a DataFrame
"""

__version__ = "0.1.1"

from .readers import (
    read_pdf,
    read_image,
    read_audio,
    read_webpage,
    read_video,
)

from .exporters import (
    to_summarized_csv,
    to_summarized_excel,
    to_summarized_json,
    summarize_dataframe,
)

from .core import OpenRouterClient
from .cache import get_cache, APICache

__all__ = [
    "read_pdf",
    "read_image",
    "read_audio",
    "read_webpage",
    "read_video",
    "to_summarized_csv",
    "to_summarized_excel",
    "to_summarized_json",
    "summarize_dataframe",
    "OpenRouterClient",
    "get_cache",
    "APICache",
]
