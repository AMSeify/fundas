"""
Tests for fundas.readers.video module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

from fundas.readers import read_video


class TestReadVideo:
    """Tests for read_video function."""

    @patch("cv2.VideoCapture")
    @patch("fundas.readers.video._get_client")
    def test_read_video_success(self, mock_get_client, mock_video_capture):
        """Test successful video reading."""
        mock_video = Mock()
        mock_video.get.side_effect = lambda prop: {
            0: 30.0,  # CAP_PROP_FPS
            7: 300,  # CAP_PROP_FRAME_COUNT
            3: 1920,  # CAP_PROP_FRAME_WIDTH
            4: 1080,  # CAP_PROP_FRAME_HEIGHT
        }.get(prop, 0)
        mock_video.read.return_value = (False, None)
        mock_video.release = Mock()
        mock_video_capture.return_value = mock_video

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "scene": ["Opening"],
            "timestamp": ["00:00"],
        }
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            df = read_video(tmp_path, prompt="Extract scenes", from_="pics")

            assert isinstance(df, pd.DataFrame)
            mock_video.release.assert_called_once()
            mock_client.extract_structured_data.assert_called_once()
        finally:
            os.unlink(tmp_path)

    def test_read_video_file_not_found(self):
        """Test reading non-existent video file."""
        with pytest.raises(FileNotFoundError):
            read_video("nonexistent.mp4")

    @patch("cv2.VideoCapture")
    @patch("fundas.readers.video._get_client")
    def test_read_video_from_audios(self, mock_get_client, mock_video_capture):
        """Test video reading with audio extraction."""
        mock_video = Mock()
        mock_video.get.side_effect = lambda prop: {
            0: 30.0,
            7: 300,
            3: 1920,
            4: 1080,
        }.get(prop, 0)
        mock_video.read.return_value = (False, None)
        mock_video.release = Mock()
        mock_video_capture.return_value = mock_video

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {"data": ["value"]}
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            read_video(tmp_path, from_="audios", api_key="test-key")

            # Check that content mentions audio analysis
            call_args = mock_client.extract_structured_data.call_args
            content = call_args[0][0]
            assert "Audio Analysis" in content
        finally:
            os.unlink(tmp_path)

    @patch("cv2.VideoCapture")
    @patch("fundas.readers.video._get_client")
    def test_read_video_from_both(self, mock_get_client, mock_video_capture):
        """Test video reading with both pics and audio."""
        mock_video = Mock()
        mock_video.get.side_effect = lambda prop: {
            0: 30.0,
            7: 300,
            3: 1920,
            4: 1080,
        }.get(prop, 0)
        mock_video.read.return_value = (False, None)
        mock_video.release = Mock()
        mock_video_capture.return_value = mock_video

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {"data": ["value"]}
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            read_video(tmp_path, from_="both", api_key="test-key")

            # Check that content mentions both frame and audio analysis
            call_args = mock_client.extract_structured_data.call_args
            content = call_args[0][0]
            assert "Frame Analysis" in content
            assert "Audio Analysis" in content
        finally:
            os.unlink(tmp_path)

    def test_read_video_invalid_from_option(self):
        """Test video reading with invalid from_ option."""
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError, match="Invalid 'from_' option"):
                read_video(tmp_path, from_="invalid", api_key="test-key")
        finally:
            os.unlink(tmp_path)

    @patch("cv2.VideoCapture")
    @patch("fundas.readers.video._get_client")
    def test_read_video_custom_sample_rate(self, mock_get_client, mock_video_capture):
        """Test video reading with custom sample rate."""
        mock_video = Mock()
        mock_video.get.side_effect = lambda prop: {
            0: 30.0,
            7: 300,
            3: 1920,
            4: 1080,
        }.get(prop, 0)
        mock_video.set = Mock()
        mock_video.read.return_value = (False, None)
        mock_video.release = Mock()
        mock_video_capture.return_value = mock_video

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {"data": ["value"]}
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            read_video(tmp_path, from_="pics", sample_rate=60, api_key="test-key")

            # Check that sample rate is mentioned in content
            call_args = mock_client.extract_structured_data.call_args
            content = call_args[0][0]
            assert "60" in content or "Sampling" in content
        finally:
            os.unlink(tmp_path)
