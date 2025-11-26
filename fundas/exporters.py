"""
Exporter module for Fundas.

This module provides functions to export DataFrames to various formats
with AI-powered transformation and summarization.
"""

import pandas as pd
from typing import Optional, Union
from pathlib import Path

from .core import OpenRouterClient


def _get_client(
    api_key: Optional[str] = None, model: Optional[str] = None
) -> OpenRouterClient:
    """Get or create an OpenRouter client instance."""
    default_model = model or "openai/gpt-3.5-turbo"
    return OpenRouterClient(api_key=api_key, model=default_model)


def to_summarized_csv(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Export DataFrame to CSV.

    Note: AI-powered transformation is planned for future release.
    Currently exports the DataFrame as-is.

    Args:
        df: DataFrame to export
        filepath: Path to save the CSV file
        prompt: Reserved for future AI transformation (not yet implemented)
        api_key: Optional OpenRouter API key (not yet used)
        model: Optional AI model to use (not yet used)
        **kwargs: Additional arguments passed to df.to_csv()

    Examples:
        >>> df = pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 87]})
        >>> to_summarized_csv(df, "output.csv")
    """
    # TODO: Implement AI-powered transformation when prompt is provided
    if prompt:
        import warnings

        warnings.warn(
            "AI-powered transformation is not yet implemented. "
            "DataFrame will be exported as-is.",
            FutureWarning,
        )

    df.to_csv(filepath, **kwargs)


def to_summarized_excel(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    prompt: Optional[str] = None,
    sheet_name: str = "Sheet1",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Export DataFrame to Excel.

    Note: AI-powered transformation is planned for future release.
    Currently exports the DataFrame as-is.

    Args:
        df: DataFrame to export
        filepath: Path to save the Excel file
        prompt: Reserved for future AI transformation (not yet implemented)
        sheet_name: Name of the Excel sheet
        api_key: Optional OpenRouter API key (not yet used)
        model: Optional AI model to use (not yet used)
        **kwargs: Additional arguments passed to df.to_excel()

    Examples:
        >>> df = pd.DataFrame({"product": ["A", "B"], "sales": [1000, 1500]})
        >>> to_summarized_excel(df, "output.xlsx")
    """
    # TODO: Implement AI-powered transformation when prompt is provided
    if prompt:
        import warnings

        warnings.warn(
            "AI-powered transformation is not yet implemented. "
            "DataFrame will be exported as-is.",
            FutureWarning,
        )

    df.to_excel(filepath, sheet_name=sheet_name, **kwargs)


def to_summarized_json(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    orient: str = "records",
    **kwargs,
) -> None:
    """
    Export DataFrame to JSON.

    Note: AI-powered transformation is planned for future release.
    Currently exports the DataFrame as-is.

    Args:
        df: DataFrame to export
        filepath: Path to save the JSON file
        prompt: Reserved for future AI transformation (not yet implemented)
        api_key: Optional OpenRouter API key (not yet used)
        model: Optional AI model to use (not yet used)
        orient: Format of JSON (see pandas.DataFrame.to_json)
        **kwargs: Additional arguments passed to df.to_json()

    Examples:
        >>> df = pd.DataFrame({"id": [1, 2], "value": [100, 200]})
        >>> to_summarized_json(df, "output.json")
    """
    # TODO: Implement AI-powered transformation when prompt is provided
    if prompt:
        import warnings

        warnings.warn(
            "AI-powered transformation is not yet implemented. "
            "DataFrame will be exported as-is.",
            FutureWarning,
        )

    df.to_json(filepath, orient=orient, **kwargs)


def summarize_dataframe(
    df: pd.DataFrame,
    prompt: str = "Provide a summary of this data",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    """
    Generate an AI-powered summary of a DataFrame.

    Args:
        df: DataFrame to summarize
        prompt: Prompt describing what kind of summary to generate
        api_key: Optional OpenRouter API key
        model: Optional AI model to use

    Returns:
        AI-generated summary of the DataFrame

    Examples:
        >>> df = pd.DataFrame({"sales": [100, 200, 150], "region": ["A", "B", "A"]})
        >>> summary = summarize_dataframe(df, prompt="Summarize sales by region")
        >>> print(summary)
    """
    client = _get_client(api_key, model)

    # Convert DataFrame to string representation with statistics
    df_str = f"Data:\n{df.to_string()}\n\nStatistics:\n{df.describe().to_string()}"

    system_prompt = (
        "You are a data analysis assistant. "
        "Provide a clear, concise summary of the data based on the user's "
        "request."
    )

    response = client.process_content(df_str, prompt, system_prompt)

    # Extract text from response
    if "choices" in response and len(response["choices"]) > 0:
        return response["choices"][0]["message"]["content"]

    return "Unable to generate summary"
