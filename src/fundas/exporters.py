"""
Exporter module for Fundas.

This module provides backward compatibility with the old exporters.py location.
The exporters have been moved to the fundas.exporters package.
"""

# Re-export all exporters from new location for backward compatibility
from .exporters import (
    to_summarized_csv,
    to_summarized_excel,
    to_summarized_json,
    summarize_dataframe,
    _get_client,
)

__all__ = [
    "to_summarized_csv",
    "to_summarized_excel",
    "to_summarized_json",
    "summarize_dataframe",
    "_get_client",
]
