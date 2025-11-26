"""
Tests for fundas.readers.audio module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

from fundas.readers import read_audio


class TestReadAudio:
    """Tests for read_audio function."""

    @patch("fundas.readers.audio._get_client")
    def test_read_audio_success(self, mock_get_client):
        """Test successful audio reading."""
        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "speaker": ["Alice"],
            "topic": ["Meeting notes"],
        }
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(b"fake audio data")

        try:
            df = read_audio(tmp_path, prompt="Extract speaker and topics")

            assert isinstance(df, pd.DataFrame)
            assert "speaker" in df.columns
            mock_client.extract_structured_data.assert_called_once()
        finally:
            os.unlink(tmp_path)

    def test_read_audio_file_not_found(self):
        """Test reading non-existent audio file."""
        with pytest.raises(FileNotFoundError):
            read_audio("nonexistent.mp3")

    @patch("fundas.readers.audio._get_client")
    def test_read_audio_with_columns(self, mock_get_client):
        """Test audio reading with specified columns."""
        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "timestamp": ["00:00"],
            "text": ["Hello"],
        }
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            read_audio(tmp_path, columns=["timestamp", "text"], api_key="test-key")

            call_args = mock_client.extract_structured_data.call_args
            assert call_args[0][2] == ["timestamp", "text"]
        finally:
            os.unlink(tmp_path)
