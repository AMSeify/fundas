# Audio Reader

The `read_audio()` function extracts structured data from audio files using local Whisper transcription or OpenRouter's audio-capable models.

## Basic Usage

```python
import fundas as fd

# Local Whisper (default)
df = fd.read_audio("meeting.mp3", prompt="Extract speaker names and key points")

# OpenRouter (better for non-English)
df = fd.read_audio(
    "audio.mp3",
    prompt="Transcribe and extract data",
    use_openrouter=True,
    model="google/gemini-2.5-flash"
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | str/Path | Required | Path to the audio file |
| `prompt` | str | "Transcribe this audio..." | Instructions for extraction |
| `columns` | list | None | Column names to extract |
| `schema` | Schema | None | Schema for typed output |
| `api_key` | str | None | OpenRouter API key |
| `model` | str | None | AI model |
| `language` | str | None | Language specification |
| `whisper_model` | str | "base" | Whisper model size |
| `device` | str | None | "cpu" or "cuda" |
| `use_openrouter` | bool | False | Send audio to OpenRouter |

## Transcription Methods

### Local Whisper (Default)

Uses OpenAI's Whisper model locally for transcription, then sends text to LLM:

```python
df = fd.read_audio(
    "meeting.mp3",
    prompt="Extract action items",
    whisper_model="medium",  # Better for non-English
    language="en"            # ISO language code
)
```

**Whisper model sizes:**
- `tiny` - Fastest, lowest accuracy
- `base` - Good balance (default)
- `small` - Better accuracy
- `medium` - High accuracy
- `large` / `large-v2` / `large-v3` - Best accuracy

### OpenRouter (Recommended for Non-English)

Sends audio directly to audio-capable models:

```python
df = fd.read_audio(
    "persian_audio.mp3",
    prompt="Extract lyrics and artist names",
    use_openrouter=True,
    model="google/gemini-2.5-flash",
    language="Persian"  # Full language name
)
```

## Language Support

### Local Whisper
Use ISO language codes:
```python
df = fd.read_audio("audio.mp3", language="fa")  # Persian
df = fd.read_audio("audio.mp3", language="ar")  # Arabic
df = fd.read_audio("audio.mp3", language="es")  # Spanish
```

Common codes: `en`, `fa`, `ar`, `es`, `fr`, `de`, `zh`, `ja`, `ko`

### OpenRouter
Use full language names:
```python
df = fd.read_audio(
    "audio.mp3",
    use_openrouter=True,
    language="Persian"
)
```

## Examples

### Meeting Transcription

```python
df = fd.read_audio(
    "meeting.mp3",
    prompt="Extract speaker names, timestamps, and key discussion points",
    columns=["speaker", "timestamp", "point"],
    whisper_model="medium"
)
```

### Persian Song Analysis

```python
df = fd.read_audio(
    "persian_song.mp3",
    prompt="Extract each verse with artist name",
    columns=["verse_number", "artist", "lyrics"],
    use_openrouter=True,
    model="google/gemini-2.5-flash",
    language="Persian"
)
```

### Interview Extraction

```python
from fundas import Schema, Column, DataType

schema = Schema([
    Column("question", DataType.STRING),
    Column("answer", DataType.STRING),
    Column("timestamp", DataType.STRING),
])

df = fd.read_audio(
    "interview.wav",
    prompt="Extract questions and answers from this interview",
    schema=schema
)
```

## Supported Formats

### Local Whisper
MP3, WAV, FLAC, OGG, M4A, and more

### OpenRouter
MP3, WAV

## GPU Acceleration

Use CUDA for faster transcription:

```python
df = fd.read_audio(
    "audio.mp3",
    prompt="Transcribe",
    device="cuda"  # Use GPU
)
```

Falls back to CPU automatically if CUDA fails.

## Dependencies

### Local Whisper
```bash
pip install openai-whisper
```

Also requires `ffmpeg` system package:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### OpenRouter
No additional dependencies, but requires an audio-capable model.

## Audio-Capable Models

For `use_openrouter=True`:
- `google/gemini-2.5-flash` (recommended)
- Check [OpenRouter models](https://openrouter.ai/models?input_modalities=audio) for current list

## Error Handling

```python
try:
    df = fd.read_audio("audio.mp3", prompt="Transcribe")
except FileNotFoundError:
    print("Audio file not found")
except RuntimeError as e:
    print(f"Error processing audio: {e}")
```
