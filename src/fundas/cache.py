"""
Caching system for Fundas API calls.

This module provides caching functionality to store and retrieve results
from OpenRouter API calls, reducing redundant processing and API costs.
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any


class APICache:
    """
    Cache for storing API responses.

    The cache stores responses based on a hash of the file content,
    prompt, and model used. This prevents re-processing the same file
    with the same prompt.
    """

    def __init__(
        self, cache_dir: Optional[str] = None, ttl: int = 86400  # 24 hours default
    ):
        """
        Initialize the API cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.fundas/cache
            ttl: Time-to-live for cache entries in seconds (default: 24 hours)
        """
        if cache_dir is None:
            cache_dir = os.path.join(os.path.expanduser("~"), ".fundas", "cache")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.enabled = True

    def _generate_key(
        self, content: str, prompt: str, model: str, columns: Optional[list] = None
    ) -> str:
        """
        Generate a unique cache key based on input parameters.

        Args:
            content: The content being processed
            prompt: The prompt used
            model: The model used
            columns: Optional column specification

        Returns:
            SHA256 hash as cache key
        """
        # Create a composite string from all parameters
        key_data = {
            "content": content,
            "prompt": prompt,
            "model": model,
            "columns": columns,
        }
        key_string = json.dumps(key_data, sort_keys=True)

        # Generate hash
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(
        self, content: str, prompt: str, model: str, columns: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result if it exists and is not expired.

        Args:
            content: The content being processed
            prompt: The prompt used
            model: The model used
            columns: Optional column specification

        Returns:
            Cached data if available and valid, None otherwise
        """
        if not self.enabled:
            return None

        cache_key = self._generate_key(content, prompt, model, columns)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)

            # Check if cache entry has expired
            timestamp = cached_data.get("timestamp", 0)
            if time.time() - timestamp > self.ttl:
                # Cache expired, remove file
                cache_file.unlink()
                return None

            return cached_data.get("data")

        except (json.JSONDecodeError, IOError):
            # Corrupted or inaccessible cache file
            return None

    def set(
        self,
        content: str,
        prompt: str,
        model: str,
        data: Dict[str, Any],
        columns: Optional[list] = None,
    ) -> None:
        """
        Store result in cache.

        Args:
            content: The content that was processed
            prompt: The prompt that was used
            model: The model that was used
            data: The data to cache
            columns: Optional column specification
        """
        if not self.enabled:
            return

        cache_key = self._generate_key(content, prompt, model, columns)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_entry = {"timestamp": time.time(), "data": data}

        try:
            with open(cache_file, "w") as f:
                json.dump(cache_entry, f)
        except IOError:
            # Fail silently if cache cannot be written
            pass

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of cache entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except IOError:
                pass
        return count

    def clear_expired(self) -> int:
        """
        Clear expired cache entries.

        Returns:
            Number of expired entries cleared
        """
        count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)

                timestamp = cached_data.get("timestamp", 0)
                if current_time - timestamp > self.ttl:
                    cache_file.unlink()
                    count += 1
            except (json.JSONDecodeError, IOError):
                # Remove corrupted files
                try:
                    cache_file.unlink()
                    count += 1
                except IOError:
                    pass

        return count

    def disable(self) -> None:
        """Disable caching."""
        self.enabled = False

    def enable(self) -> None:
        """Enable caching."""
        self.enabled = True


# Global cache instance
_global_cache: Optional[APICache] = None


def get_cache(cache_dir: Optional[str] = None, ttl: int = 86400) -> APICache:
    """
    Get or create the global cache instance.

    Args:
        cache_dir: Directory to store cache files
        ttl: Time-to-live for cache entries in seconds

    Returns:
        The global APICache instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = APICache(cache_dir=cache_dir, ttl=ttl)

    return _global_cache
