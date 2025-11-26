"""
Tests for fundas.readers.image module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

from fundas.readers import read_image


class TestReadImage:
    """Tests for read_image function."""

    @patch("PIL.Image.open")
    @patch("fundas.readers.image._get_client")
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
    @patch("fundas.readers.image._get_client")
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
            read_image(tmp_path, model="anthropic/claude-3-opus", api_key="test-key")

            mock_get_client.assert_called_once_with(
                "test-key", "anthropic/claude-3-opus"
            )
        finally:
            os.unlink(tmp_path)

    @patch("PIL.Image.open")
    @patch("fundas.readers.image._get_client")
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
    @patch("fundas.readers.image._get_client")
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
    @patch("fundas.readers.image._get_client")
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
