# Video Reader

The `read_video()` function extracts structured data from video files by analyzing frames and/or audio tracks.

## Basic Usage

```python
import fundas as fd

df = fd.read_video(
    "presentation.mp4",
    prompt="Extract slide titles and timestamps",
    from_="pics"
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | str/Path | Required | Path to the video file |
| `prompt` | str | "Analyze this video..." | Instructions for extraction |
| `from_` | str/list | "both" | Source: "pics", "audios", or "both" |
| `columns` | list | None | Column names to extract |
| `schema` | Schema | None | Schema for typed output |
| `api_key` | str | None | OpenRouter API key |
| `model` | str | None | AI model |
| `sample_rate` | int | 30 | Extract 1 frame per N frames |

## Extraction Sources

### Frames Only (`from_="pics"`)

Analyzes video frames:

```python
df = fd.read_video(
    "presentation.mp4",
    prompt="Extract text from each slide",
    from_="pics"
)
```

### Audio Only (`from_="audios"`)

Analyzes audio track:

```python
df = fd.read_video(
    "lecture.mp4",
    prompt="Extract speaker's key points",
    from_="audios"
)
```

### Both (`from_="both"`)

Combines frame and audio analysis:

```python
df = fd.read_video(
    "interview.mp4",
    prompt="Extract questions, answers, and visual context",
    from_="both"
)
```

## Examples

### Presentation Analysis

```python
df = fd.read_video(
    "slides.mp4",
    prompt="Extract slide titles and key points from each slide",
    columns=["slide_number", "title", "key_points"],
    from_="pics",
    sample_rate=60  # Sample every 2 seconds at 30fps
)
```

### Lecture Transcription

```python
df = fd.read_video(
    "lecture.mp4",
    prompt="Extract topics discussed with timestamps",
    columns=["timestamp", "topic", "summary"],
    from_="audios"
)
```

### Interview Extraction

```python
from fundas import Schema, Column, DataType

schema = Schema([
    Column("timestamp", DataType.STRING),
    Column("speaker", DataType.STRING),
    Column("statement", DataType.STRING),
])

df = fd.read_video(
    "interview.mp4",
    prompt="Extract each statement with speaker and timestamp",
    schema=schema,
    from_="both"
)
```

### Scene Detection

```python
df = fd.read_video(
    "movie_clip.mp4",
    prompt="Identify scene changes with descriptions",
    columns=["timestamp", "scene_description", "characters"],
    from_="pics",
    sample_rate=15  # Sample every 0.5 seconds
)
```

## Sample Rate

The `sample_rate` parameter controls frame sampling:

```python
# Every frame (high detail, slow)
df = fd.read_video("video.mp4", sample_rate=1)

# Every 30 frames (~1 second at 30fps)
df = fd.read_video("video.mp4", sample_rate=30)

# Every 60 frames (~2 seconds at 30fps)
df = fd.read_video("video.mp4", sample_rate=60)
```

Lower values = more frames = more detail but slower processing.

## Video Metadata

The reader automatically extracts:
- Duration
- Frame rate (FPS)
- Resolution (width × height)
- Total frame count

## Current Limitations

- **Frame Analysis**: Currently provides frame descriptions based on timestamps. Full OCR/vision analysis requires additional integration.
- **Audio Analysis**: Provides metadata. Full transcription requires audio processing services.

## Dependencies

```bash
pip install opencv-python
```

## Supported Formats

Most common video formats:
- MP4
- AVI
- MOV
- MKV
- WebM

## Error Handling

```python
try:
    df = fd.read_video("video.mp4", from_="pics")
except FileNotFoundError:
    print("Video file not found")
except ValueError as e:
    print(f"Invalid from_ option: {e}")
except RuntimeError as e:
    print(f"Error analyzing video: {e}")
```

## Tips

- Use higher `sample_rate` for long videos
- Use `from_="pics"` for visual content
- Use `from_="audios"` for spoken content
- Combine both for comprehensive analysis
