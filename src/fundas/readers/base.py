"""
Base utilities for Fundas readers.

This module provides shared helper functions used by all reader functions.
"""

import pandas as pd
from typing import Optional, List, TYPE_CHECKING

from ..client import OpenRouterClient

if TYPE_CHECKING:
    from ..schema import Schema


def _get_client(
    api_key: Optional[str] = None, model: Optional[str] = None
) -> OpenRouterClient:
    """
    Get or create an OpenRouter client instance.

    Args:
        api_key: Optional API key for OpenRouter
        model: Optional model name to use

    Returns:
        OpenRouterClient instance
    """
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
            from ..schema import DataType

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
