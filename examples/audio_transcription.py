"""
Test audio transcription and extraction with read_audio function.

Tests both English and Persian audio files to verify multilingual support.

Usage:
    python examples/test_audio.py

Two transcription methods:
1. Local Whisper (default): Uses openai-whisper locally
   - Requires: pip install openai-whisper and ffmpeg
   - Use language codes: "en", "fa", "es", etc.

2. OpenRouter API (use_openrouter=True): Sends audio to cloud models
   - Requires: OPENROUTER_API_KEY environment variable
   - Use audio-capable models like "google/gemini-2.5-flash"
   - Use full language names: "Persian", "English", "Arabic", etc.
   - Often better for non-English languages
"""

import os
import sys
import warnings

# Suppress the CUDA warning when using CPU intentionally
warnings.filterwarnings(
    "ignore", message="Performing inference on CPU when CUDA is available"
)

# Add parent directory to path for local development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fundas import read_audio  # noqa: E402

# Use CPU to avoid CUDA issues (set to None to auto-detect, or "cuda" for GPU)
DEVICE = "cpu"

# Audio-capable model for OpenRouter
AUDIO_MODEL = "google/gemini-2.5-flash"


def test_english_audio():
    """Test English audio transcription (Harvard sentences)."""
    print("=" * 60)
    print("Testing English Audio: harvard.wav")
    print("=" * 60)

    try:
        # English transcription with language explicitly set
        df = read_audio(
            "examples/harvard.wav",
            prompt="Transcribe the audio and extract each sentence as a separate row",
            columns=["sentence_number", "sentence_text"],
            language="en",  # English - set explicitly for best accuracy
            whisper_model="base",
            device=DEVICE,
        )

        print("\nExtracted DataFrame:")
        print(df.to_string())
        print(f"\nShape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


def test_persian_audio_whisper():
    """Test Persian/Farsi audio transcription with local Whisper."""
    print("\n" + "=" * 60)
    print("Testing Persian Audio with Local Whisper: RayayeMA.mp3")
    print("(Detecting artist names like Ebi, Shadmehr)")
    print("=" * 60)

    try:
        # Persian transcription - MUST set language="fa" for Persian
        # Use "medium" or "large" model for better non-English accuracy
        df = read_audio(
            "examples/RayayeMA.mp3",
            prompt="""This is a Persian (Farsi) audio file.
Transcribe the Persian lyrics accurately.
Extract information about each verse or section.
If artist names like Ebi, Shadmehr, or others are mentioned, identify them.
Create a separate row for each verse or distinct section of the audio.""",
            columns=[
                "verse_number",
                "artist_name",
                "persian_lyrics",
                "verse_description",
            ],
            language="fa",  # IMPORTANT: Set Persian language for accurate transcription
            whisper_model="medium",  # Use medium or large for non-English
            device=DEVICE,
        )

        print("\nExtracted DataFrame:")
        print(df.to_string())
        print(f"\nShape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


def test_persian_with_openrouter():
    """Test Persian audio using OpenRouter API with audio-capable model."""
    print("\n" + "=" * 60)
    print("Testing Persian Audio with OpenRouter API: RayayeMA.mp3")
    print(f"Using model: {AUDIO_MODEL}")
    print("=" * 60)

    try:
        # Use OpenRouter API with audio-capable model
        # This sends the audio directly to the model for transcription + extraction
        df = read_audio(
            "examples/RayayeMA.mp3",
            prompt="""This is a Persian (Farsi) song.
Listen carefully and extract:
1. Each verse or section as a separate row
2. Any artist names mentioned (e.g., Ebi, Shadmehr Aghili)
3. The Persian lyrics for each verse
4. A brief description of each section's theme or emotion""",
            columns=["verse_number", "artist", "lyrics_persian", "description"],
            language="Persian",  # Full language name for OpenRouter models
            use_openrouter=True,  # Send audio directly to cloud model
            model=AUDIO_MODEL,  # Audio-capable model
        )

        print("\nExtracted DataFrame (via OpenRouter):")
        print(df.to_string())
        print(f"\nShape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


def test_english_with_openrouter():
    """Test English audio using OpenRouter API."""
    print("\n" + "=" * 60)
    print("Testing English Audio with OpenRouter API: harvard.wav")
    print(f"Using model: {AUDIO_MODEL}")
    print("=" * 60)

    try:
        df = read_audio(
            "examples/harvard.wav",
            prompt="Transcribe this audio and extract each sentence as a separate row",
            columns=["sentence_number", "sentence_text"],
            language="English",
            use_openrouter=True,
            model=AUDIO_MODEL,
        )

        print("\nExtracted DataFrame (via OpenRouter):")
        print(df.to_string())
        print(f"\nShape: {df.shape}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


def test_raw_transcription():
    """Test getting raw transcription without complex extraction."""
    print("\n" + "=" * 60)
    print("Testing Raw Transcription: Both files")
    print("=" * 60)

    # Test English with local Whisper
    print("\n--- English (harvard.wav) - Local Whisper ---")
    try:
        df = read_audio(
            "examples/harvard.wav",
            prompt="Return the complete transcription as text",
            columns=["transcription"],
            language="en",
            whisper_model="base",
            device=DEVICE,
        )
        print(df.to_string())
    except Exception as e:
        print(f"Error: {e}")

    # Test Persian with OpenRouter (better for non-English)
    print("\n--- Persian (RayayeMA.mp3) - OpenRouter API ---")
    print(f"Using model: {AUDIO_MODEL}")
    try:
        df = read_audio(
            "examples/RayayeMA.mp3",
            prompt="Transcribe this Persian audio completely and accurately",
            columns=["transcription"],
            language="Persian",
            use_openrouter=True,
            model=AUDIO_MODEL,
        )
        print(df.to_string())
    except Exception as e:
        print(f"Error: {e}")


def test_artist_extraction_openrouter():
    """Test extracting artist and song info from Persian audio using OpenRouter."""
    print("\n" + "=" * 60)
    print("Testing Artist/Song Extraction from Persian Audio (OpenRouter)")
    print(f"Using model: {AUDIO_MODEL}")
    print("=" * 60)

    try:
        df = read_audio(
            "examples/RayayeMA.mp3",
            prompt="""This is a Persian music audio file.
Listen carefully and extract:
1. Any artist names mentioned (like Ebi, Shadmehr Aghili, etc.)
2. Song sections or verses
3. Key themes or emotions in each section
4. The Persian lyrics for each part

Return each distinct section as a separate row.
If multiple artists are mentioned, list them separately.""",
            columns=["section_number", "artist", "theme", "lyrics_excerpt_persian"],
            language="Persian",
            use_openrouter=True,
            model=AUDIO_MODEL,
        )

        print("\nArtist/Song Extraction:")
        print(df.to_string())
        print(f"\nNumber of sections extracted: {len(df)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("Fundas Audio Transcription Test")
    print("================================")
    print("Testing multilingual audio support\n")
    print("Methods available:")
    print("  1. Local Whisper - requires openai-whisper + ffmpeg")
    print("  2. OpenRouter API - requires OPENROUTER_API_KEY")
    print()

    # Check if files exist
    if not os.path.exists("examples/harvard.wav"):
        print("Warning: examples/harvard.wav not found!")
    if not os.path.exists("examples/RayayeMA.mp3"):
        print("Warning: examples/RayayeMA.mp3 not found!")

    # Check for API key
    if os.environ.get("OPENROUTER_API_KEY"):
        print("✓ OPENROUTER_API_KEY found")
    else:
        print("⚠ OPENROUTER_API_KEY not set - OpenRouter tests will fail")

    # Run tests
    print("\n" + "=" * 60)
    print("[1] Raw Transcription Test")
    print("=" * 60)
    test_raw_transcription()

    print("\n" + "=" * 60)
    print("[2] English Audio Test (Local Whisper)")
    print("=" * 60)
    test_english_audio()

    print("\n" + "=" * 60)
    print("[3] English Audio Test (OpenRouter API)")
    print("=" * 60)
    test_english_with_openrouter()

    print("\n" + "=" * 60)
    print("[4] Persian Audio Test (OpenRouter - Recommended)")
    print("=" * 60)
    test_persian_with_openrouter()

    print("\n" + "=" * 60)
    print("[5] Persian Artist Extraction (OpenRouter)")
    print("=" * 60)
    test_artist_extraction_openrouter()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
