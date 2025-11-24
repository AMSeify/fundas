#!/usr/bin/env python
"""
Example usage of the fundas library.

This script demonstrates how to use each of the main functions.
Note: Requires OPENROUTER_API_KEY environment variable to be set.
"""

import fundas as fd
import os


def main():
    print("Fundas Library Examples")
    print("=" * 50)
    print(f"Version: {fd.__version__}")
    print()

    # Check if API key is available
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️  OPENROUTER_API_KEY not set. The functions won't work without it.")
        print("   Set it with: export OPENROUTER_API_KEY='your-api-key'")
        print()

    print("Available functions:")
    print("  - fd.read_pdf(filepath, prompt)")
    print("  - fd.read_image(filepath, prompt)")
    print("  - fd.read_audio(filepath, prompt)")
    print("  - fd.read_webpage(url, prompt)")
    print("  - fd.read_video(filepath, prompt, from_=['pics', 'audios', 'both'])")
    print()

    print("Example usage:")
    print()

    print("# Read PDF file")
    print("df = fd.read_pdf('invoice.pdf', prompt='Extract invoice items')")
    print()

    print("# Read image file")
    print("df = fd.read_image('chart.png', prompt='Extract data from chart')")
    print()

    print("# Read audio file")
    print("df = fd.read_audio('meeting.mp3', prompt='Extract key discussion points')")
    print()

    print("# Read webpage")
    print("df = fd.read_webpage('https://example.com', prompt='Extract main content')")
    print()

    print("# Read video file")
    print("df = fd.read_video('video.mp4', prompt='Extract key scenes', from_='pics')")
    print(
        "df = fd.read_video('video.mp4', prompt='Extract audio content', from_='audios')"
    )
    print("df = fd.read_video('video.mp4', prompt='Extract all content', from_='both')")
    print()

    print("All functions return pandas DataFrames for immediate analysis!")


if __name__ == "__main__":
    main()
