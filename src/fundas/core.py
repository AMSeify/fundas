"""
Fundas - AI-powered data import library using OpenRouter API

This module provides backward compatibility with the old core.py location.
The OpenRouterClient has been moved to fundas.client.

Core functionality for communicating with OpenRouter API to extract
structured data from various file types.
"""

# Re-export OpenRouterClient from new location for backward compatibility
from .client import OpenRouterClient

__all__ = ["OpenRouterClient"]
