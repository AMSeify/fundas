"""
Tests for fundas.readers module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

from fundas.readers import (
    read_pdf,
    read_image,
    read_audio,
    read_webpage,
    read_video,
    _get_client,
)


class TestGetClient:
    """Tests for _get_client helper function."""

    @patch.dict("os.environ", {}, clear=True)
    def test_get_client_default_model(self):
        """Test getting client with default model."""
        client = _get_client(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.model == "openai/gpt-3.5-turbo"

    def test_get_client_custom_model(self):
        """Test getting client with custom model."""
        client = _get_client(api_key="test-key", model="anthropic/claude-3-opus")
        assert client.model == "anthropic/claude-3-opus"


class TestReadPdf:
    """Tests for read_pdf function."""

    @patch("PyPDF2.PdfReader")
    @patch("fundas.readers._get_client")
    def test_read_pdf_success(self, mock_get_client, mock_pdf_reader):
        """Test successful PDF reading."""
        # Setup mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        # Setup mock client
        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "item": ["Product A"],
            "price": ["$10"],
        }
        mock_get_client.return_value = mock_client

        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            df = read_pdf(tmp_path, prompt="Extract items and prices")

            assert isinstance(df, pd.DataFrame)
            assert "item" in df.columns
            assert "price" in df.columns
            assert len(df) == 1
            mock_client.extract_structured_data.assert_called_once()
        finally:
            os.unlink(tmp_path)

    def test_read_pdf_file_not_found(self):
        """Test reading non-existent PDF file."""
        with pytest.raises(FileNotFoundError):
            read_pdf("nonexistent.pdf")

    @patch("PyPDF2.PdfReader")
    @patch("fundas.readers._get_client")
    def test_read_pdf_with_columns(self, mock_get_client, mock_pdf_reader):
        """Test PDF reading with specified columns."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "name": ["John"],
            "age": ["30"],
        }
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            df = read_pdf(tmp_path, columns=["name", "age"])

            assert isinstance(df, pd.DataFrame)
            call_args = mock_client.extract_structured_data.call_args
            assert call_args[0][2] == ["name", "age"]
        finally:
            os.unlink(tmp_path)

    @patch("PyPDF2.PdfReader")
    def test_read_pdf_extraction_error(self, mock_pdf_reader):
        """Test handling of PDF extraction errors."""
        mock_pdf_reader.side_effect = Exception("PDF Error")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with pytest.raises(RuntimeError, match="Error reading PDF file"):
                read_pdf(tmp_path, api_key="test-key")
        finally:
            os.unlink(tmp_path)


class TestReadImage:
    """Tests for read_image function."""

    @patch("PIL.Image.open")
    @patch("fundas.readers._get_client")
    def test_read_image_success(self, mock_get_client, mock_image_open):
        """Test successful image reading."""
        mock_img_instance = Mock()
        mock_img_instance.size = (800, 600)
        mock_img_instance.format = "PNG"
        mock_img_instance.mode = "RGB"
        mock_image_open.return_value = mock_img_instance

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {
            "object": ["Car"],
            "color": ["Red"],
        }
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            df = read_image(tmp_path, prompt="Describe the image")

            assert isinstance(df, pd.DataFrame)
            assert "object" in df.columns
            mock_client.extract_structured_data.assert_called_once()
        finally:
            os.unlink(tmp_path)

    def test_read_image_file_not_found(self):
        """Test reading non-existent image file."""
        with pytest.raises(FileNotFoundError):
            read_image("nonexistent.png")

    @patch("PIL.Image.open")
    @patch("fundas.readers._get_client")
    def test_read_image_with_custom_model(self, mock_get_client, mock_image_open):
        """Test image reading with custom model."""
        mock_img_instance = Mock()
        mock_img_instance.size = (800, 600)
        mock_img_instance.format = "PNG"
        mock_img_instance.mode = "RGB"
        mock_image_open.return_value = mock_img_instance

        mock_client = Mock()
        mock_client.extract_structured_data.return_value = {"data": ["value"]}
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            read_image(
                tmp_path,
                model="anthropic/claude-3-opus",
                api_key="test-key",
            )

            mock_get_client.assert_called_once_with(
                "test-key", "anthropic/claude-3-opus"
            )
        finally:
            os.unlink(tmp_path)

    @patch("PIL.Image.open")
    @patch("fundas.readers._get_client")
    def test_read_image_ocr_mode_with_language(self, mock_get_client, mock_image_open):
        """Test OCR mode with custom language."""
        # Mock pytesseract at the import level
        with patch.dict("sys.modules", {"pytesseract": Mock()}):
            import sys

            mock_pytesseract = sys.modules["pytesseract"]
            mock_pytesseract.image_to_string = Mock(
                return_value="Extracted Arabic text"
            )

            mock_img_instance = Mock()
            mock_img_instance.size = (800, 600)
            mock_img_instance.format = "PNG"
            mock_img_instance.mode = "RGB"
            mock_image_open.return_value = mock_img_instance

            mock_client = Mock()
            mock_client.extract_structured_data.return_value = {
                "text": ["Arabic content"]
            }
            mock_get_client.return_value = mock_client

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                df = read_image(
                    tmp_path, prompt="Extract text", mode="ocr", language="ara"
                )

                assert isinstance(df, pd.DataFrame)
                # Verify tesseract was called with correct language parameter
                mock_pytesseract.image_to_string.assert_called_once()
                call_kwargs = mock_pytesseract.image_to_string.call_args[1]
                assert call_kwargs.get("lang") == "ara"
                mock_client.extract_structured_data.assert_called_once()
            finally:
                os.unlink(tmp_path)

    @patch("builtins.open", create=True)
    @patch("PIL.Image.open")
    @patch("fundas.readers._get_client")
    def test_read_image_direct_mode(self, mock_get_client, mock_image_open, mock_open):
        """Test direct mode with vision model."""
        # Mock image file reading
        mock_img_instance = Mock()
        mock_img_instance.format = "PNG"
        mock_image_open.return_value = mock_img_instance

        # Mock file reading for base64 encoding
        mock_file = Mock()
        mock_file.read.return_value = b"fake_image_data"
        mock_open.return_value.__enter__.return_value = mock_file

        mock_client = Mock()
        mock_client.extract_structured_data_from_image.return_value = {
            "description": ["A beautiful scene"],
            "objects": ["tree, sky, road"],
        }
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            df = read_image(
                tmp_path,
                prompt="Describe the scene",
                mode="direct",
                model="openai/gpt-4-vision-preview",
            )

            assert isinstance(df, pd.DataFrame)
            assert "description" in df.columns
            # Verify the vision extraction method was called
            mock_client.extract_structured_data_from_image.assert_called_once()
            # Verify it was called with base64 image data
            call_args = mock_client.extract_structured_data_from_image.call_args
            assert call_args[0][0].startswith("data:image/png;base64,")
        finally:
            os.unlink(tmp_path)

    def test_read_image_invalid_mode(self):
        """Test error handling for invalid mode."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError, match="Invalid mode"):
                read_image(tmp_path, mode="invalid_mode", api_key="test-key")
        finally:
            os.unlink(tmp_path)

    @patch("PIL.Image.open")
    @patch("fundas.readers._get_client")
    def test_read_image_ocr_mode_default(self, mock_get_client, mock_image_open):
        """Test OCR mode as default with default English language."""
        with patch.dict("sys.modules", {"pytesseract": Mock()}):
            import sys

            mock_pytesseract = sys.modules["pytesseract"]
            mock_pytesseract.image_to_string = Mock(
                return_value="Extracted English text"
            )

            mock_img_instance = Mock()
            mock_img_instance.size = (800, 600)
            mock_img_instance.format = "PNG"
            mock_img_instance.mode = "RGB"
            mock_image_open.return_value = mock_img_instance

            mock_client = Mock()
            mock_client.extract_structured_data.return_value = {
                "text": ["English content"]
            }
            mock_get_client.return_value = mock_client

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # Don't specify mode, should default to OCR
                df = read_image(tmp_path, prompt="Extract text")

                assert isinstance(df, pd.DataFrame)
                # Verify default language is 'eng'
                call_kwargs = mock_pytesseract.image_to_string.call_args[1]
                assert call_kwargs.get("lang") == "eng"
            finally:
                os.unlink(tmp_path)


class TestReadAudio:
    """Tests for read_audio function."""

    @patch("fundas.readers._get_client")
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

    @patch("fundas.readers._get_client")
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


class TestReadWebpage:
    """Tests for read_webpage function."""

    @patch("requests.Session.get")
    @patch("fundas.readers._get_client")
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
    @patch("fundas.readers._get_client")
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
            "https://example.com",
            columns=["title", "author"],
            api_key="test-key",
        )

        call_args = mock_client.extract_structured_data.call_args
        assert call_args[0][2] == ["title", "author"]


class TestReadVideo:
    """Tests for read_video function."""

    @patch("cv2.VideoCapture")
    @patch("fundas.readers._get_client")
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
    @patch("fundas.readers._get_client")
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
    @patch("fundas.readers._get_client")
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
    @patch("fundas.readers._get_client")
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
