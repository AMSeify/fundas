"""
Tests for fundas.core module.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fundas.core import OpenRouterClient


class TestOpenRouterClient:
    """Tests for OpenRouterClient class."""
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = OpenRouterClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.model == "openai/gpt-3.5-turbo"
    
    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        client = OpenRouterClient(api_key="test-key", model="anthropic/claude-3-opus")
        assert client.model == "anthropic/claude-3-opus"
    
    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenRouter API key is required"):
                OpenRouterClient()
    
    def test_init_with_env_api_key(self):
        """Test initialization with API key from environment."""
        with patch.dict('os.environ', {'OPENROUTER_API_KEY': 'env-key'}):
            client = OpenRouterClient()
            assert client.api_key == "env-key"
    
    @patch('fundas.core.requests.post')
    def test_process_content_success(self, mock_post):
        """Test successful content processing."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.process_content("test content", "test prompt")
        
        assert result["choices"][0]["message"]["content"] == "Test response"
        mock_post.assert_called_once()
    
    @patch('fundas.core.requests.post')
    def test_process_content_with_system_prompt(self, mock_post):
        """Test content processing with system prompt."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.process_content(
            "test content", 
            "test prompt", 
            system_prompt="test system prompt"
        )
        
        # Check that post was called with correct structure
        call_args = mock_post.call_args
        messages = call_args[1]['json']['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
    
    @patch('fundas.core.requests.post')
    def test_process_content_api_error(self, mock_post):
        """Test handling of API errors."""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        client = OpenRouterClient(api_key="test-key")
        with pytest.raises(RuntimeError, match="Error communicating with OpenRouter API"):
            client.process_content("test content", "test prompt")
    
    @patch('fundas.core.requests.post')
    def test_extract_structured_data_json_response(self, mock_post):
        """Test extracting structured data with JSON response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"name": ["John"], "age": ["30"]}'
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.extract_structured_data("test content", "extract data")
        
        assert result == {"name": ["John"], "age": ["30"]}
    
    @patch('fundas.core.requests.post')
    def test_extract_structured_data_markdown_json(self, mock_post):
        """Test extracting structured data from markdown-wrapped JSON."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '```json\n{"name": ["John"], "age": ["30"]}\n```'
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.extract_structured_data("test content", "extract data")
        
        assert result == {"name": ["John"], "age": ["30"]}
    
    @patch('fundas.core.requests.post')
    def test_extract_structured_data_with_columns(self, mock_post):
        """Test extracting structured data with specified columns."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"name": ["John"], "age": ["30"]}'
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.extract_structured_data(
            "test content", 
            "extract data",
            columns=["name", "age"]
        )
        
        assert "name" in result
        assert "age" in result
        
        # Verify system prompt included columns
        call_args = mock_post.call_args
        messages = call_args[1]['json']['messages']
        system_msg = messages[0]['content']
        assert "name" in system_msg
        assert "age" in system_msg
    
    @patch('fundas.core.requests.post')
    def test_extract_structured_data_invalid_json(self, mock_post):
        """Test extracting structured data with invalid JSON response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": 'This is not valid JSON'
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        client = OpenRouterClient(api_key="test-key")
        result = client.extract_structured_data("test content", "extract data")
        
        # Should return raw text in structured format
        assert "content" in result
        assert result["content"][0] == "This is not valid JSON"
