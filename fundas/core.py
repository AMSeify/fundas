"""
Fundas - AI-powered data import library using OpenRouter API

Core functionality for communicating with OpenRouter API to extract
structured data from various file types.
"""

import os
import time
import json
import requests
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dotenv import load_dotenv

from .cache import get_cache

import fundas

if TYPE_CHECKING:
    from fundas.schema import Schema

# Load environment variables from .env file
load_dotenv()


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 86400,
        max_retries: int = 3,
        retry_delay: int = 1,
    ):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key. If not provided, reads from
                OPENROUTER_API_KEY env variable.
            model: The AI model to use for processing. If not provided,
                reads from OPENROUTER_MODEL env variable.
                Default is openai/gpt-3.5-turbo.
            use_cache: Whether to use caching for API responses.
                Default is True.
            cache_ttl: Cache time-to-live in seconds.
                Default is 86400 (24 hours).
            max_retries: Maximum number of retries for failed API calls.
                Default is 3.
            retry_delay: Delay between retries in seconds. Default is 1.
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Set OPENROUTER_API_KEY "
                "environment variable or pass api_key parameter."
            )
        self.model = model or os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.use_cache = use_cache
        self.cache = get_cache(ttl=cache_ttl) if use_cache else None
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def process_content(
        self,
        content: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send content to OpenRouter API for processing.

        Args:
            content: The content to process (text, description, etc.)
            prompt: User prompt describing what to extract
            system_prompt: Optional system prompt to guide the AI
            response_format: Optional response format for structured outputs
                (e.g., {"type": "json_schema", "json_schema": {...}})

        Returns:
            Response from the API containing extracted data

        Raises:
            RuntimeError: If API communication fails after all retries
            ValueError: If the model is not supported or request is invalid
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append(
            {
                "role": "user",
                "content": f"{prompt}\n\nContent to analyze:\n{content}",
            }
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
        }

        # Add response_format for structured outputs if provided
        if response_format:
            payload["response_format"] = response_format

        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url, headers=headers, json=payload, timeout=60
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                # Check for specific error codes
                if e.response and e.response.status_code == 400:
                    raise ValueError(f"Invalid request: {str(e)}") from e
                elif e.response and e.response.status_code == 401:
                    raise ValueError("Invalid API key") from e
                elif e.response and e.response.status_code == 404:
                    raise ValueError(f"Model not found: {self.model}") from e
                last_exception = e
            except requests.exceptions.RequestException as e:
                last_exception = e

            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff

        # All retries failed
        raise RuntimeError(
            "Error communicating with OpenRouter API after "
            f"{self.max_retries} attempts: {str(last_exception)}"
        )

    def process_content_with_image(
        self, image_base64: str, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send image content to OpenRouter API for processing using vision models.

        Args:
            image_base64: Base64-encoded image data with data URI prefix
            prompt: User prompt describing what to extract
            system_prompt: Optional system prompt to guide the AI

        Returns:
            Response from the API containing extracted data

        Raises:
            RuntimeError: If API communication fails after all retries
            ValueError: If the model is not supported or request is invalid
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_base64}},
                ],
            }
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
        }

        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url, headers=headers, json=payload, timeout=60
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                # Check for specific error codes
                if e.response and e.response.status_code == 400:
                    raise ValueError(f"Invalid request: {str(e)}") from e
                elif e.response and e.response.status_code == 401:
                    raise ValueError("Invalid API key") from e
                elif e.response and e.response.status_code == 404:
                    raise ValueError(f"Model not found: {self.model}") from e
                last_exception = e
            except requests.exceptions.RequestException as e:
                last_exception = e

            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff

        # All retries failed
        raise RuntimeError(
            f"Error communicating with OpenRouter API after "
            f"{self.max_retries} attempts: {str(last_exception)}"
        )

    def extract_structured_data(
        self, content: str, prompt: str, columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from content based on user prompt.

        Args:
            content: The content to analyze
            prompt: User prompt describing what to extract
            columns: Optional list of column names to extract

        Returns:
            Dictionary containing extracted structured data

        Raises:
            RuntimeError: If API communication fails
            ValueError: If request parameters are invalid
        """
        # Check cache first
        if self.use_cache and self.cache:
            cached_data = self.cache.get(content, prompt, self.model, columns)
            if cached_data is not None:
                return cached_data

        system_prompt = (
            "You are a data extraction assistant. "
            "Extract structured data from the provided content "
            "and return it in a JSON format that can be easily converted "
            "to a pandas DataFrame. "
            "Each key should be a column name and each value should be "
            "a list of values."
        )

        if columns:
            system_prompt += f"\n\nExtract the following columns: {', '.join(columns)}"

        full_prompt = (
            f"{prompt}\n\n"
            "Return the data as a JSON object where keys are column names "
            "and values are lists. "
            "If extracting single values, wrap them in a list. "
            "Example format:\n"
            '{"column1": ["value1"], "column2": ["value2"]}'
        )

        response = self.process_content(content, full_prompt, system_prompt)

        # Extract the response text
        if "choices" in response and len(response["choices"]) > 0:
            response_text = response["choices"][0]["message"]["content"]

            # Try to parse JSON from the response
            try:
                # Look for JSON in the response
                # (it might be wrapped in markdown code blocks)
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    json_str = response_text.strip()

                data = json.loads(json_str)

                # Normalize data: ensure all arrays have the same length
                if isinstance(data, dict):
                    # Find the maximum length
                    max_len = max(
                        (len(v) if isinstance(v, list) else 1 for v in data.values()),
                        default=1,
                    )
                    # Pad shorter arrays with None or repeat last value
                    normalized_data = {}
                    for key, value in data.items():
                        if isinstance(value, list):
                            if len(value) < max_len:
                                # Pad with None
                                normalized_data[key] = value + [None] * (
                                    max_len - len(value)
                                )
                            else:
                                normalized_data[key] = value
                        else:
                            # Convert single values to list
                            normalized_data[key] = [value] * max_len
                    data = normalized_data

                # Cache the result
                if self.use_cache and self.cache:
                    self.cache.set(content, prompt, self.model, data, columns)

                return data
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw text in a structured format
                result = {"content": [response_text]}

                # Cache even the fallback result
                if self.use_cache and self.cache:
                    self.cache.set(content, prompt, self.model, result, columns)

                return result

        return {"content": ["No response from API"]}

    def extract_structured_data_with_schema(
        self,
        content: str,
        prompt: str,
        schema: "fundas.schema.Schema",
        use_strict_schema: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract structured data using a defined schema with type enforcement.

        This method uses OpenRouter's structured outputs feature to ensure
        responses conform to the specified JSON Schema and converts values
        to the appropriate Python types.

        Args:
            content: The content to analyze
            prompt: User prompt describing what to extract
            schema: Schema object defining columns and their types
            use_strict_schema: Whether to use strict schema mode (default: True)
                Set to False for models that don't support structured outputs

        Returns:
            Dictionary containing extracted and type-converted structured data

        Raises:
            RuntimeError: If API communication fails
            ValueError: If request parameters are invalid

        Examples:
            >>> from fundas.schema import Schema, Column, DataType
            >>> schema = Schema([
            ...     Column("name", DataType.STRING),
            ...     Column("price", DataType.FLOAT),
            ...     Column("quantity", DataType.INTEGER),
            ... ])
            >>> data = client.extract_structured_data_with_schema(
            ...     content, prompt, schema
            ... )
        """
        # Get column names from schema
        columns = schema.get_column_names()

        # Check cache first (include schema name in cache key)
        cache_key_columns = columns + [f"__schema:{schema.name}"]
        if self.use_cache and self.cache:
            cached_data = self.cache.get(content, prompt, self.model, cache_key_columns)
            if cached_data is not None:
                # Apply type conversion even for cached data
                return schema.convert_data(cached_data)

        system_prompt = (
            "You are a data extraction assistant. "
            "Extract structured data from the provided content "
            "and return it as a valid JSON object. "
            "Each key should be a column name and each value should be "
            "an array of values for that column."
        )

        # Add column descriptions if available
        col_descriptions = []
        for col in schema.columns:
            desc = f"- {col.name} ({col.dtype.value})"
            if col.description:
                desc += f": {col.description}"
            col_descriptions.append(desc)

        system_prompt += (
            "\n\nExtract these columns with specified types:\n"
            + "\n".join(col_descriptions)
        )

        full_prompt = (
            f"{prompt}\n\n"
            "Return the data as a JSON object where keys are column names "
            "and values are arrays. Ensure values match the specified types. "
            "For dates, use ISO format (YYYY-MM-DD). "
            "For datetime, use ISO 8601 format."
        )

        # Prepare response_format for structured outputs
        response_format = None
        if use_strict_schema:
            response_format = schema.to_response_format()

        try:
            response = self.process_content(
                content, full_prompt, system_prompt, response_format
            )
        except ValueError as e:
            # If structured output fails (model doesn't support it),
            # fall back to regular extraction
            if "Invalid request" in str(e) or "400" in str(e):
                response = self.process_content(content, full_prompt, system_prompt)
            else:
                raise

        # Extract the response text
        if "choices" in response and len(response["choices"]) > 0:
            response_text = response["choices"][0]["message"]["content"]

            # Try to parse JSON from the response
            try:
                # Look for JSON in the response
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    json_str = response_text.strip()

                data = json.loads(json_str)

                # Normalize data: ensure all arrays have the same length
                if isinstance(data, dict):
                    max_len = max(
                        (len(v) if isinstance(v, list) else 1 for v in data.values()),
                        default=1,
                    )
                    normalized_data = {}
                    for key, value in data.items():
                        if isinstance(value, list):
                            if len(value) < max_len:
                                normalized_data[key] = value + [None] * (
                                    max_len - len(value)
                                )
                            else:
                                normalized_data[key] = value
                        else:
                            normalized_data[key] = [value] * max_len
                    data = normalized_data

                # Cache the raw result (before type conversion)
                if self.use_cache and self.cache:
                    self.cache.set(content, prompt, self.model, data, cache_key_columns)

                # Apply type conversion from schema
                converted_data = schema.convert_data(data)

                return converted_data

            except json.JSONDecodeError:
                result = {"content": [response_text]}
                if self.use_cache and self.cache:
                    self.cache.set(
                        content, prompt, self.model, result, cache_key_columns
                    )
                return result

        return {"content": ["No response from API"]}

    def process_content_with_audio(
        self,
        audio_filepath: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send audio content to OpenRouter API for processing.

        This method sends audio files directly to audio-capable models
        like google/gemini-2.5-flash via OpenRouter's input_audio content type.

        Args:
            audio_filepath: Path to the audio file (mp3, wav)
            prompt: User prompt describing what to extract/transcribe
            system_prompt: Optional system prompt to guide the AI
            language: Optional language hint (e.g., "Persian", "English")

        Returns:
            Response from the API containing extracted data

        Raises:
            RuntimeError: If API communication fails after all retries
            ValueError: If the model is not supported or request is invalid
            FileNotFoundError: If the audio file doesn't exist
        """
        from pathlib import Path
        import base64

        filepath = Path(audio_filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_filepath}")

        # Read and encode the audio file
        with open(filepath, "rb") as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        # Determine format based on file extension (only wav and mp3 supported)
        extension = filepath.suffix.lower().lstrip(".")
        if extension not in ["wav", "mp3"]:
            # Convert extension to supported format name
            extension = "mp3"  # Default to mp3 for other formats

        # Build prompt with language hint if provided
        full_prompt = prompt
        if language:
            full_prompt = f"[Language: {language}] {prompt}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": full_prompt},
                    {
                        "type": "input_audio",
                        "input_audio": {"data": audio_base64, "format": extension},
                    },
                ],
            }
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
        }

        # Retry logic with longer timeout for audio
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=180,
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if e.response and e.response.status_code == 400:
                    error_msg = str(e)
                    try:
                        error_detail = e.response.json()
                        error_msg = error_detail.get("error", {}).get("message", str(e))
                    except Exception:
                        pass
                    raise ValueError(f"Invalid request: {error_msg}") from e
                elif e.response and e.response.status_code == 401:
                    raise ValueError("Invalid API key") from e
                elif e.response and e.response.status_code == 404:
                    raise ValueError(f"Model not found: {self.model}") from e
                last_exception = e
            except requests.exceptions.RequestException as e:
                last_exception = e

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))

        raise RuntimeError(
            f"Error processing audio after {self.max_retries} attempts: "
            f"{str(last_exception)}"
        )

    def extract_structured_data_from_audio(
        self,
        audio_filepath: str,
        prompt: str,
        columns: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured data from audio using audio-capable models.

        This method sends audio directly to models that support audio input
        (like google/gemini-2.5-flash) and extracts structured data.

        Args:
            audio_filepath: Path to the audio file (mp3, wav)
            prompt: User prompt describing what to extract
            columns: Optional list of column names to extract
            language: Optional language hint (e.g., "Persian", "Farsi", "English")

        Returns:
            Dictionary containing extracted structured data

        Raises:
            RuntimeError: If API communication fails
            ValueError: If request parameters are invalid
        """
        # Check cache first
        cache_key = f"audio:{audio_filepath}"
        if self.use_cache and self.cache:
            cached_data = self.cache.get(cache_key, prompt, self.model, columns)
            if cached_data is not None:
                return cached_data

        system_prompt = (
            "You are an audio transcription and data extraction assistant. "
            "Listen to the audio carefully and extract structured data based on "
            "the user's request. "
            "Return it in a JSON format that can be easily converted "
            "to a pandas DataFrame. "
            "Each key should be a column name and each value should be "
            "a list of values."
        )

        if columns:
            system_prompt += f"\n\nExtract the following columns: {', '.join(columns)}"

        full_prompt = (
            f"{prompt}\n\n"
            "Return the data as a JSON object where keys are column names "
            "and values are lists. "
            "If extracting single values, wrap them in a list. "
            "For each distinct section or item, add a new element to each list. "
            "Example format:\n"
            '{"column1": ["value1", "value2"], "column2": ["value1", "value2"]}'
        )

        response = self.process_content_with_audio(
            audio_filepath, full_prompt, system_prompt, language
        )

        # Extract the response text
        if "choices" in response and len(response["choices"]) > 0:
            response_text = response["choices"][0]["message"]["content"]

            # Try to parse JSON from the response
            try:
                # Look for JSON in the response
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    json_str = response_text.strip()

                data = json.loads(json_str)

                # Normalize data: ensure all arrays have the same length
                if isinstance(data, dict):
                    max_len = max(
                        (len(v) if isinstance(v, list) else 1 for v in data.values()),
                        default=1,
                    )
                    normalized_data = {}
                    for key, value in data.items():
                        if isinstance(value, list):
                            if len(value) < max_len:
                                normalized_data[key] = value + [None] * (
                                    max_len - len(value)
                                )
                            else:
                                normalized_data[key] = value
                        else:
                            normalized_data[key] = [value] * max_len
                    data = normalized_data

                # Cache the result
                if self.use_cache and self.cache:
                    self.cache.set(cache_key, prompt, self.model, data, columns)

                return data

            except json.JSONDecodeError:
                result = {"content": [response_text]}
                if self.use_cache and self.cache:
                    self.cache.set(cache_key, prompt, self.model, result, columns)
                return result

        return {"content": ["No response from API"]}

    def extract_structured_data_from_image(
        self, image_base64: str, prompt: str, columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from image using vision models.

        Args:
            image_base64: Base64-encoded image data with data URI prefix
            prompt: User prompt describing what to extract
            columns: Optional list of column names to extract

        Returns:
            Dictionary containing extracted structured data

        Raises:
            RuntimeError: If API communication fails
            ValueError: If request parameters are invalid
        """
        # Check cache first (use image data as content key)
        if self.use_cache and self.cache:
            cached_data = self.cache.get(image_base64, prompt, self.model, columns)
            if cached_data is not None:
                return cached_data

        system_prompt = (
            "You are a data extraction assistant. "
            "Analyze the image and extract structured data based on "
            "the user's request. "
            "Return it in a JSON format that can be easily converted "
            "to a pandas DataFrame. "
            "Each key should be a column name and each value should be "
            "a list of values."
        )

        if columns:
            system_prompt += f"\n\nExtract the following columns: {', '.join(columns)}"

        full_prompt = (
            f"{prompt}\n\n"
            "Return the data as a JSON object where keys are column names "
            "and values are lists. "
            "If extracting single values, wrap them in a list. "
            "Example format:\n"
            '{"column1": ["value1"], "column2": ["value2"]}'
        )

        response = self.process_content_with_image(
            image_base64, full_prompt, system_prompt
        )

        # Extract the response text
        if "choices" in response and len(response["choices"]) > 0:
            response_text = response["choices"][0]["message"]["content"]

            # Try to parse JSON from the response
            try:
                # Look for JSON in the response
                # (it might be wrapped in markdown code blocks)
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    json_str = response_text.strip()

                data = json.loads(json_str)

                # Normalize data to ensure all arrays have the same length
                if isinstance(data, dict):
                    # Find the maximum length among all arrays
                    max_length = max(
                        (len(v) if isinstance(v, list) else 1 for v in data.values()),
                        default=1,
                    )

                    # Pad shorter arrays with None
                    for key, value in data.items():
                        if isinstance(value, list):
                            if len(value) < max_length:
                                data[key] = value + [None] * (max_length - len(value))
                        else:
                            # If value is not a list, convert it to a list
                            data[key] = [value] + [None] * (max_length - 1)

                # Cache the result
                if self.use_cache and self.cache:
                    self.cache.set(image_base64, prompt, self.model, data, columns)

                return data
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw text in a structured format
                result = {"content": [response_text]}

                # Cache even the fallback result
                if self.use_cache and self.cache:
                    self.cache.set(image_base64, prompt, self.model, result, columns)

                return result

        return {"content": ["No response from API"]}
