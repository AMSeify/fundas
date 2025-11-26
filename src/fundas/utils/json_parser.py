"""
JSON parsing utilities for Fundas.

This module provides functions to parse JSON from LLM responses,
including handling markdown-wrapped JSON and data normalization.
"""

import json
from typing import Dict, Any


def parse_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON from an LLM response text.

    Handles both plain JSON and markdown-wrapped JSON (```json blocks).

    Args:
        response_text: The raw response text from the LLM

    Returns:
        Parsed dictionary, or {"content": [response_text]} if parsing fails
    """
    try:
        # Look for JSON in the response (it might be wrapped in markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text.strip()

        return json.loads(json_str)
    except json.JSONDecodeError:
        # If JSON parsing fails, return raw text in a structured format
        return {"content": [response_text]}


def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize data to ensure all arrays have the same length.

    Args:
        data: Dictionary where values may be lists of different lengths

    Returns:
        Normalized dictionary with all lists padded to the same length
    """
    if not isinstance(data, dict):
        return data

    # Find the maximum length among all arrays
    max_len = max(
        (len(v) if isinstance(v, list) else 1 for v in data.values()),
        default=1,
    )

    # Pad shorter arrays with None or convert single values to lists
    normalized_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            if len(value) < max_len:
                # Pad with None
                normalized_data[key] = value + [None] * (max_len - len(value))
            else:
                normalized_data[key] = value
        else:
            # Convert single values to list
            normalized_data[key] = [value] * max_len

    return normalized_data
