"""
Shared fixtures for Fundas tests.

This module provides common test fixtures and utilities.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def temp_pdf():
    """Create a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def temp_image():
    """Create a temporary image file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def temp_audio():
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write(b"fake audio data")
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def temp_video():
    """Create a temporary video file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def temp_excel():
    """Create a temporary Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def temp_json():
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def mock_openrouter_response():
    """Create a mock OpenRouter API response."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"data": ["value"]}'}}]
    }
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture
def mock_openrouter_client():
    """Create a mock OpenRouterClient."""
    mock_client = Mock()
    mock_client.extract_structured_data.return_value = {"data": ["value"]}
    mock_client.extract_structured_data_from_image.return_value = {"data": ["value"]}
    mock_client.extract_structured_data_from_audio.return_value = {"data": ["value"]}
    mock_client.process_content.return_value = {
        "choices": [{"message": {"content": "Summary"}}]
    }
    return mock_client
