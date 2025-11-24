"""
Tests for fundas.exporters module.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from fundas.exporters import (
    to_summarized_csv,
    to_summarized_excel,
    to_summarized_json,
    summarize_dataframe,
    _get_client,
)

# Check if openpyxl is available for Excel tests
try:
    import openpyxl

    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


class TestGetClient:
    """Tests for _get_client helper function."""

    def test_get_client_default_model(self):
        """Test getting client with default model."""
        client = _get_client(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.model == "openai/gpt-3.5-turbo"

    def test_get_client_custom_model(self):
        """Test getting client with custom model."""
        client = _get_client(api_key="test-key", model="anthropic/claude-3-opus")
        assert client.model == "anthropic/claude-3-opus"


class TestToSummarizedCsv:
    """Tests for to_summarized_csv function."""

    def test_csv_export_without_prompt(self):
        """Test CSV export without AI summarization."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
            tmp_path = tmp.name

        try:
            to_summarized_csv(df, tmp_path, index=False)

            # Verify file was created and contains data
            assert Path(tmp_path).exists()
            result_df = pd.read_csv(tmp_path)
            assert len(result_df) == 2
            assert list(result_df.columns) == ["name", "age"]
        finally:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)

    @patch("fundas.exporters._get_client")
    def test_csv_export_with_prompt(self, mock_get_client):
        """Test CSV export with AI summarization."""
        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})

        mock_client = Mock()
        mock_response = {
            "choices": [{"message": {"content": "Transform data suggestion"}}]
        }
        mock_client.process_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
            tmp_path = tmp.name

        try:
            to_summarized_csv(
                df,
                tmp_path,
                prompt="Summarize by category",
                api_key="test-key",
                index=False,
            )

            # Verify API was called
            mock_client.process_content.assert_called_once()

            # Verify file was created
            assert Path(tmp_path).exists()
        finally:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)


class TestToSummarizedExcel:
    """Tests for to_summarized_excel function."""

    @pytest.mark.skipif(not HAS_OPENPYXL, reason="openpyxl not installed")
    def test_excel_export_without_prompt(self):
        """Test Excel export without AI summarization."""
        df = pd.DataFrame({"product": ["A", "B"], "sales": [100, 200]})

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            to_summarized_excel(df, tmp_path, index=False)

            # Verify file was created
            assert Path(tmp_path).exists()

            # Verify contents
            result_df = pd.read_excel(tmp_path)
            assert len(result_df) == 2
            assert list(result_df.columns) == ["product", "sales"]
        finally:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)

    @pytest.mark.skipif(not HAS_OPENPYXL, reason="openpyxl not installed")
    @patch("fundas.exporters._get_client")
    def test_excel_export_with_prompt(self, mock_get_client):
        """Test Excel export with AI summarization."""
        df = pd.DataFrame({"product": ["A", "B"], "sales": [100, 200]})

        mock_client = Mock()
        mock_response = {
            "choices": [{"message": {"content": "Transform data suggestion"}}]
        }
        mock_client.process_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            to_summarized_excel(
                df, tmp_path, prompt="Add totals row", api_key="test-key", index=False
            )

            # Verify API was called
            mock_client.process_content.assert_called_once()

            # Verify file was created
            assert Path(tmp_path).exists()
        finally:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)


class TestToSummarizedJson:
    """Tests for to_summarized_json function."""

    def test_json_export_without_prompt(self):
        """Test JSON export without AI summarization."""
        df = pd.DataFrame({"id": [1, 2], "value": [100, 200]})

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
            tmp_path = tmp.name

        try:
            to_summarized_json(df, tmp_path, orient="records")

            # Verify file was created
            assert Path(tmp_path).exists()

            # Verify contents
            result_df = pd.read_json(tmp_path, orient="records")
            assert len(result_df) == 2
            assert list(result_df.columns) == ["id", "value"]
        finally:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)

    @patch("fundas.exporters._get_client")
    def test_json_export_with_prompt(self, mock_get_client):
        """Test JSON export with AI summarization."""
        df = pd.DataFrame({"id": [1, 2], "value": [100, 200]})

        mock_client = Mock()
        mock_response = {
            "choices": [{"message": {"content": "Transform data suggestion"}}]
        }
        mock_client.process_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
            tmp_path = tmp.name

        try:
            to_summarized_json(
                df, tmp_path, prompt="Nest by category", api_key="test-key"
            )

            # Verify API was called
            mock_client.process_content.assert_called_once()

            # Verify file was created
            assert Path(tmp_path).exists()
        finally:
            if Path(tmp_path).exists():
                os.unlink(tmp_path)


class TestSummarizeDataframe:
    """Tests for summarize_dataframe function."""

    @patch("fundas.exporters._get_client")
    def test_summarize_dataframe_success(self, mock_get_client):
        """Test successful DataFrame summarization."""
        df = pd.DataFrame({"sales": [100, 200, 150], "region": ["A", "B", "A"]})

        mock_client = Mock()
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Region A has average sales of 125, Region B has 200"
                    }
                }
            ]
        }
        mock_client.process_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        summary = summarize_dataframe(
            df, prompt="Summarize by region", api_key="test-key"
        )

        assert "Region A" in summary
        assert "Region B" in summary
        mock_client.process_content.assert_called_once()

    @patch("fundas.exporters._get_client")
    def test_summarize_dataframe_no_response(self, mock_get_client):
        """Test DataFrame summarization with no API response."""
        df = pd.DataFrame({"data": [1, 2, 3]})

        mock_client = Mock()
        mock_response = {}  # Empty response
        mock_client.process_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        summary = summarize_dataframe(df, api_key="test-key")

        assert summary == "Unable to generate summary"
