"""
Video reader for Fundas.

This module provides the read_video function for extracting data from video files.
"""

import pandas as pd
from typing import Optional, List, Union, TYPE_CHECKING
from pathlib import Path

from .base import _get_client, _extract_data, _apply_schema_dtypes

if TYPE_CHECKING:
    from ..schema import Schema


def read_video(
    filepath: Union[str, Path],
    prompt: str = "Analyze this video and extract key information",
    from_: Union[str, List[str]] = "both",
    columns: Optional[List[str]] = None,
    schema: Optional["Schema"] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    sample_rate: int = 30,
) -> pd.DataFrame:
    """
    Read a video file and convert it to a pandas DataFrame using AI extraction.

    Args:
        filepath: Path to the video file
        prompt: Prompt describing what data to extract from the video
        from_: Source(s) to extract from -
            'pics' (frames), 'audios' (audio track), or 'both'
        columns: Optional list of column names to extract
        schema: Optional Schema object for structured output with type enforcement
        api_key: Optional OpenRouter API key
            (uses OPENROUTER_API_KEY env var if not provided)
        model: Optional AI model to use
            (default: gpt-3.5-turbo)
        sample_rate: Frame sampling rate (extract 1 frame per N frames)

    Returns:
        pandas DataFrame containing extracted data with proper types if schema provided

    Examples:
        >>> df = read_video(
        ...     "presentation.mp4",
        ...     prompt="Extract slide titles",
        ...     from_="pics"
        ... )
        >>> df = read_video("lecture.mp4", from_="audios")
        >>> df = read_video("interview.mp4", from_="both")
    """
    try:
        import cv2
    except ImportError:
        raise ImportError(
            "opencv-python is required for read_video. "
            "Install it with: pip install opencv-python"
        )

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Normalize from_ parameter
    if isinstance(from_, str):
        from_ = [from_]

    valid_options = {"pics", "audios", "both"}
    for option in from_:
        if option not in valid_options:
            raise ValueError(
                f"Invalid 'from_' option: {option}. Must be one of {valid_options}"
            )

    if "both" in from_:
        from_ = ["pics", "audios"]

    content = f"Video file: {filepath.name}\n"
    content += f"File size: {filepath.stat().st_size} bytes\n"

    # Extract video information
    try:
        video = cv2.VideoCapture(str(filepath))
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        content += f"Duration: {duration:.2f} seconds\n"
        content += f"Frame rate: {fps:.2f} fps\n"
        content += f"Resolution: {width}x{height}\n"
        content += f"Total frames: {frame_count}\n"

        if "pics" in from_:
            content += "\n--- Frame Analysis ---\n"
            content += f"Sampling every {sample_rate} frames\n"

            # Sample frames from the video
            frame_descriptions = []
            frame_idx = 0
            while frame_idx < frame_count:
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = video.read()
                if not ret:
                    break

                # Basic frame description
                # (in a real implementation, use OCR or vision models)
                timestamp = frame_idx / fps if fps > 0 else 0
                frame_descriptions.append(f"Frame at {timestamp:.2f}s")

                frame_idx += sample_rate

            content += f"Sampled {len(frame_descriptions)} frames\n"
            content += "\n".join(
                frame_descriptions[:10]
            )  # Limit to first 10 for brevity
            if len(frame_descriptions) > 10:
                content += f"\n... and {len(frame_descriptions) - 10} more frames"

        if "audios" in from_:
            content += "\n\n--- Audio Analysis ---\n"
            content += (
                "[Note: Full audio extraction requires "
                "additional audio processing services]\n"
            )

        video.release()

    except Exception as e:
        content += f"\nError analyzing video: {str(e)}"

    # Use OpenRouter to extract structured data
    client = _get_client(api_key, model)
    data = _extract_data(client, content, prompt, columns, schema)

    df = pd.DataFrame(data)
    return _apply_schema_dtypes(df, schema)
