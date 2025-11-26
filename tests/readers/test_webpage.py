"""
Tests for fundas.readers.webpage module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

from fundas.readers import read_webpage


class TestReadWebpage:
    """Tests for read_webpage function."""

    @patch("requests.Session.get")
    @patch("fundas.readers.webpage._get_client")
    def test_read_webpage_success(self, mock_get_client, mock_get):
        """Test successful webpage reading."""
        mock_response = Mock()
        mock_response.content = (
            b"<html><body><h1>Title</h1><p>Content</p></body></html>"
        )
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "title": ["Title"],
            "content": ["Content"],
        }
        mock_get_client.return_value = mock_client

        df = read_webpage("https://example.com", prompt="Extract title and content")

        assert isinstance(df, pd.DataFrame)
        assert "title" in df.columns
        mock_get.assert_called_once()
        mock_client.extract_structured_data.assert_called_once()

    @patch("requests.Session.get")
    def test_read_webpage_request_error(self, mock_get):
        """Test handling of webpage request errors."""
        mock_get.side_effect = Exception("Network error")

        with pytest.raises(RuntimeError, match="Error fetching webpage"):
            read_webpage("https://example.com", api_key="test-key")

    @patch("requests.Session.get")
    @patch("fundas.readers.webpage._get_client")
    def test_read_webpage_with_columns(self, mock_get_client, mock_get):
        """Test webpage reading with specified columns."""
        mock_response = Mock()
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "title": ["Test"],
            "author": ["John"],
        }
        mock_get_client.return_value = mock_client

        read_webpage(
            "https://example.com", columns=["title", "author"], api_key="test-key"
        )

        call_args = mock_client.extract_structured_data.call_args
        assert call_args[0][2] == ["title", "author"]
