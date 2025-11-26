"""
Tests for fundas.readers.pdf module.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import tempfile
import os

from fundas.readers import read_pdf


class TestReadPdf:
    """Tests for read_pdf function."""

    @patch("PyPDF2.PdfReader")
    @patch("fundas.readers.pdf._get_client")
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
    @patch("fundas.readers.pdf._get_client")
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
