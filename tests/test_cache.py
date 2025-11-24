"""
Tests for fundas.cache module.
"""

import time
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

from fundas.cache import APICache, get_cache


class TestAPICache:
    """Tests for APICache class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = APICache(
            cache_dir=self.temp_dir, ttl=1
        )  # 1 second TTL for testing

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_cache_initialization(self):
        """Test cache initialization."""
        assert self.cache.cache_dir == Path(self.temp_dir)
        assert self.cache.ttl == 1
        assert self.cache.enabled is True
        assert self.cache.cache_dir.exists()

    def test_cache_set_and_get(self):
        """Test setting and getting cache entries."""
        data = {"name": ["John"], "age": ["30"]}
        self.cache.set("content", "prompt", "model", data)

        result = self.cache.get("content", "prompt", "model")
        assert result == data

    def test_cache_get_nonexistent(self):
        """Test getting non-existent cache entry."""
        result = self.cache.get("nonexistent", "prompt", "model")
        assert result is None

    def test_cache_expiration(self):
        """Test cache entry expiration."""
        data = {"name": ["John"]}
        self.cache.set("content", "prompt", "model", data)

        # Entry should exist
        result = self.cache.get("content", "prompt", "model")
        assert result == data

        # Wait for expiration
        time.sleep(1.1)

        # Entry should be expired
        result = self.cache.get("content", "prompt", "model")
        assert result is None

    def test_cache_with_columns(self):
        """Test cache with column specification."""
        data = {"name": ["John"], "age": ["30"]}
        self.cache.set("content", "prompt", "model", data, columns=["name", "age"])

        result = self.cache.get("content", "prompt", "model", columns=["name", "age"])
        assert result == data

        # Different columns should not match
        result = self.cache.get("content", "prompt", "model", columns=["name"])
        assert result is None

    def test_cache_different_prompts(self):
        """Test that different prompts create different cache entries."""
        data1 = {"result": ["A"]}
        data2 = {"result": ["B"]}

        self.cache.set("content", "prompt1", "model", data1)
        self.cache.set("content", "prompt2", "model", data2)

        assert self.cache.get("content", "prompt1", "model") == data1
        assert self.cache.get("content", "prompt2", "model") == data2

    def test_cache_clear(self):
        """Test clearing all cache entries."""
        self.cache.set("content1", "prompt", "model", {"data": ["A"]})
        self.cache.set("content2", "prompt", "model", {"data": ["B"]})

        count = self.cache.clear()
        assert count == 2

        assert self.cache.get("content1", "prompt", "model") is None
        assert self.cache.get("content2", "prompt", "model") is None

    def test_cache_clear_expired(self):
        """Test clearing only expired cache entries."""
        # Add entry that will expire
        self.cache.set("content1", "prompt", "model", {"data": ["A"]})

        # Wait for expiration
        time.sleep(1.1)

        # Add fresh entry
        self.cache.set("content2", "prompt", "model", {"data": ["B"]})

        count = self.cache.clear_expired()
        assert count == 1

        # Expired entry should be gone
        assert self.cache.get("content1", "prompt", "model") is None

        # Fresh entry should still exist
        assert self.cache.get("content2", "prompt", "model") == {"data": ["B"]}

    def test_cache_disable_enable(self):
        """Test disabling and enabling cache."""
        data = {"name": ["John"]}

        # Cache is enabled by default
        self.cache.set("content", "prompt", "model", data)
        assert self.cache.get("content", "prompt", "model") == data

        # Disable cache
        self.cache.disable()
        assert self.cache.enabled is False

        # Should not get cached data when disabled
        assert self.cache.get("content", "prompt", "model") is None

        # Should not set data when disabled
        self.cache.set("content2", "prompt", "model", data)
        self.cache.enable()
        assert self.cache.get("content2", "prompt", "model") is None

    def test_cache_corrupted_file(self):
        """Test handling of corrupted cache files."""
        # Create a corrupted cache file
        cache_file = self.cache.cache_dir / "corrupted.json"
        with open(cache_file, "w") as f:
            f.write("not valid json {{{")

        # Should not crash and return None
        result = self.cache.get("content", "prompt", "model")
        assert result is None

    def test_get_cache_singleton(self):
        """Test that get_cache returns a singleton instance."""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2


class TestCacheIntegration:
    """Integration tests for caching with OpenRouterClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("fundas.cache.get_cache")
    @patch("fundas.core.requests.post")
    def test_client_uses_cache(self, mock_post, mock_get_cache):
        """Test that OpenRouterClient uses cache."""
        from fundas.core import OpenRouterClient

        # Set up mock cache
        mock_cache = Mock()
        # First get() returns None (cache miss),
        # second get() returns cached data (cache hit)
        mock_cache.get.side_effect = [None, {"name": ["John"]}]
        mock_cache.set = Mock()
        mock_get_cache.return_value = mock_cache

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"name": ["John"]}'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Create client with cache - this will call get_cache()
        client = OpenRouterClient(api_key="test-key", use_cache=True, cache_ttl=10)
        # Manually set the cache to our mock
        client.cache = mock_cache

        # First call should hit the API
        result1 = client.extract_structured_data("test content", "extract data")
        assert mock_post.call_count == 1
        assert mock_cache.set.call_count == 1

        # Second call with same parameters should use cache
        result2 = client.extract_structured_data("test content", "extract data")
        assert mock_post.call_count == 1  # No additional API call

        assert result1 == result2

    @patch("fundas.core.requests.post")
    def test_client_without_cache(self, mock_post):
        """Test that OpenRouterClient can work without cache."""
        from fundas.core import OpenRouterClient

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"name": ["John"]}'}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Create client without cache
        client = OpenRouterClient(api_key="test-key", use_cache=False)

        # Each call should hit the API
        client.extract_structured_data("test content", "extract data")
        assert mock_post.call_count == 1

        client.extract_structured_data("test content", "extract data")
        assert mock_post.call_count == 2  # Second API call made
