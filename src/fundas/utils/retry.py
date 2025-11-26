"""
Retry utilities for Fundas.

This module provides retry logic with exponential backoff for API calls.
"""

import time
from typing import TypeVar, Callable, Optional
import functools

T = TypeVar("T")


def with_retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """
    Decorator that adds retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Base delay between retries in seconds
        exceptions: Tuple of exception types to catch and retry on
        on_retry: Optional callback called on each retry with (exception, attempt)

    Returns:
        Decorated function with retry logic

    Examples:
        >>> @with_retry(max_retries=3, retry_delay=1.0)
        ... def api_call():
        ...     # Make API call that may fail
        ...     pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if on_retry:
                        on_retry(e, attempt)
                    # Wait before retry (except on last attempt)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff

            # All retries failed
            raise last_exception  # type: ignore

        return wrapper

    return decorator
