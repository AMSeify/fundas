"""
Audio reader for Fundas.

This module provides the read_audio function for extracting data from audio files.
"""

import pandas as pd
from typing import Optional, List, Union, TYPE_CHECKING
from pathlib import Path

from .base import _get_client, _extract_data, _apply_schema_dtypes

if TYPE_CHECKING:
    from ..schema import Schema


def read_audio(
    filepath: Union[str, Path],
    prompt: str = "Transcribe this audio and extract key information",
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    language: Optional[str] = None,
    whisper_model: str = "base",
    device: Optional[str] = None,
    use_openrouter: bool = False,
) -> pd.DataFrame:
    """
    Read an audio file and convert it to a pandas DataFrame using AI extraction.

    This function supports two transcription methods:
    1. Local Whisper (default): Uses OpenAI's Whisper model locally for transcription,
       then sends text to LLM for structured extraction.
    2. OpenRouter API (use_openrouter=True): Sends audio directly to audio-capable
       models like google/gemini-2.5-flash for transcription and extraction in one step.

    Supports MP3 and WAV formats for OpenRouter, and additional formats (FLAC, OGG,
    M4A, etc.) for local Whisper transcription.

    Args:
        filepath: Path to the audio file
            - For OpenRouter: mp3, wav supported
            - For local Whisper: mp3, wav, flac, ogg, m4a, and more
        prompt: Prompt describing what data to extract from the audio
        columns: Optional list of column names to extract
        schema: Optional Schema object for structured output with type enforcement
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use.
            - For OpenRouter audio: use audio-capable models
              like "google/gemini-2.5-flash"
            - For local Whisper + LLM: default is "openai/gpt-3.5-turbo"
        language: Language specification for better accuracy.
            - For OpenRouter: use full name like "Persian", "Farsi",
              "English", "Arabic"
            - For local Whisper: use ISO codes like "fa", "en", "ar", "es"
            Common language codes: "en" (English), "fa" (Persian/Farsi),
            "ar" (Arabic), "es" (Spanish), "fr" (French), "de" (German),
            "zh" (Chinese)
        whisper_model: Whisper model size for local transcription
            (ignored if use_openrouter=True).
            Options: "tiny", "base", "small", "medium", "large",
            "large-v2", "large-v3"
            Default: "base". Use "medium" or "large" for non-English.
        device: Device to run local Whisper on ("cuda", "cpu", or None).
            Use "cpu" if you encounter GPU memory issues.
        use_openrouter: If True, send audio directly to OpenRouter.
            This is often more accurate for non-English languages.
            Default: False (use local Whisper)

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> # Basic transcription with local Whisper (English)
        >>> df = read_audio(
        ...     "meeting.mp3",
        ...     prompt="Extract speaker names and key points",
        ...     language="en"
        ... )

        >>> # Persian audio with local Whisper
        >>> df = read_audio(
        ...     "persian_audio.mp3",
        ...     prompt="Extract the artist name and song lyrics",
        ...     language="fa",  # Persian/Farsi code for Whisper
        ...     whisper_model="medium"  # Use larger model for non-English
        ... )

        >>> # Persian audio with OpenRouter (recommended for non-English)
        >>> df = read_audio(
        ...     "persian_song.mp3",
        ...     prompt="Extract each verse with artist name (Ebi, Shadmehr, etc.)",
        ...     columns=["verse_number", "artist", "lyrics"],
        ...     language="Persian",  # Full language name for OpenRouter
        ...     use_openrouter=True,
        ...     model="google/gemini-2.5-flash"  # Audio-capable model
        ... )

        >>> # Extract song information into multiple rows
        >>> df = read_audio(
        ...     "music.mp3",
        ...     prompt="Extract each song/verse as a separate row with artist name",
        ...     columns=["artist", "lyrics", "verse_number"],
        ...     language="Farsi",
        ...     use_openrouter=True,
        ...     model="google/gemini-2.5-flash"
        ... )
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Initialize client
    client = _get_client(api_key, model)

    if use_openrouter:
        # Send audio directly to OpenRouter audio-capable model
        # This method is better for non-English languages and complex extraction
        try:
            data = client.extract_structured_data_from_audio(
                str(filepath),
                prompt=prompt,
                columns=columns,
                language=language,
            )
            df = pd.DataFrame(data)
            return _apply_schema_dtypes(df, schema)

        except Exception as e:
            raise RuntimeError(
                f"Error processing audio with OpenRouter: {str(e)}. "
                f"Make sure you're using an audio-capable model like "
                f"'google/gemini-2.5-flash'. Check supported models at: "
                f"https://openrouter.ai/models?input_modalities=audio"
            ) from e

    else:
        # Use local Whisper for transcription, then LLM for extraction
        # Get audio file metadata
        metadata = f"Audio file: {filepath.name}\n"
        metadata += f"File size: {filepath.stat().st_size} bytes\n"
        metadata += f"File extension: {filepath.suffix}\n"

        transcription = ""
        try:
            import whisper
            import torch

            # Determine device - prefer CUDA but fall back to CPU
            if device is None:
                compute_device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                compute_device = device
            use_fp16 = compute_device == "cuda"

            # Load the Whisper model
            whisper_mdl = whisper.load_model(whisper_model, device=compute_device)

            # Transcribe with language specification
            transcribe_options = {"fp16": use_fp16}
            if language:
                transcribe_options["language"] = language
                transcribe_options["task"] = "transcribe"

            try:
                result = whisper_mdl.transcribe(str(filepath), **transcribe_options)
                transcription = result.get("text", "")
            except RuntimeError as gpu_error:
                # If CUDA fails, retry on CPU
                if compute_device == "cuda":
                    whisper_mdl = whisper.load_model(whisper_model, device="cpu")
                    transcribe_options["fp16"] = False
                    result = whisper_mdl.transcribe(str(filepath), **transcribe_options)
                    transcription = result.get("text", "")
                else:
                    raise gpu_error

            # Add language info
            detected_lang = result.get("language", "unknown")
            if not language:
                metadata += f"Detected language: {detected_lang}\n"
            else:
                metadata += f"Specified language: {language}\n"
            metadata += f"Whisper model: {whisper_model}\n"

        except ImportError:
            transcription = (
                "[Whisper not installed. Install with: pip install openai-whisper]\n"
                "[Note: You may also need ffmpeg installed on your system]\n"
                "[Alternatively, use use_openrouter=True with an audio model]"
            )
        except Exception as e:
            transcription = f"[Transcription error: {str(e)}]"

        # Combine metadata and transcription
        content = metadata + "\n--- Transcription ---\n" + transcription

        # Use LLM to extract structured data from transcription
        data = _extract_data(client, content, prompt, columns, schema)

        df = pd.DataFrame(data)
        return _apply_schema_dtypes(df, schema)
