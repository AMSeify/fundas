"""
Example demonstrating OCR and Direct modes for image reading in Fundas.

This script shows how to use both modes:
1. OCR mode - Extracts text via OCR then sends to LLM
2. Direct mode - Sends image directly to vision-capable LLM

Make sure to set your OPENROUTER_API_KEY environment variable before running.
"""

import fundas as fd
import os


def test_ocr_mode():
    """Test OCR mode with different languages"""
    print("\n" + "=" * 80)
    print("TESTING OCR MODE")
    print("=" * 80)

    # Test 1: English text image
    print("\n1. English Text (from poem):")
    print("-" * 40)
    try:
        df = fd.read_image(
            "test_images/English_OCR_sample.png",
            prompt="Extract the text from this poem",
            mode="ocr",
            language="eng",
        )
        print(df)
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Persian/Farsi text (OCR)
    print("\n2. Persian/Farsi Text (OCR):")
    print("-" * 40)
    try:
        df = fd.read_image(
            "test_images/farsi_OCR_sample.png",
            prompt="Extract and describe the text content",
            mode="ocr",
            language="fas",  # Farsi language code
        )
        print(df)
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Persian/Farsi text (Non-OCR sample)
    print("\n3. Persian/Farsi Text (Non-OCR sample):")
    print("-" * 40)
    try:
        df = fd.read_image(
            "test_images/Farsi_nonOCR_sample.png",
            prompt="Extract the Persian text content",
            mode="ocr",
            language="fas",  # Farsi language code
        )
        print(df)
    except Exception as e:
        print(f"Error: {e}")


def test_direct_mode():
    """Test Direct mode with vision-capable models"""
    print("\n" + "=" * 80)
    print("TESTING DIRECT MODE (Vision Models)")
    print("=" * 80)
    print("Note: Using openai/gpt-5-mini which supports multimodal capabilities")
    print()

    # Test 1: Scene description
    print("\n1. Robot Scene Description:")
    print("-" * 40)
    try:
        df = fd.read_image(
            "test_images/Photo_describeing_sample.png",
            prompt=(
                "Describe the scene in detail. "
                "What is the robot doing? What's the atmosphere?"
            ),
            mode="direct",
            model="openai/gpt-5-mini",  # Multimodal model
        )
        print(df)
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Extract structured data from visual content
    print("\n2. Extract Details from Image:")
    print("-" * 40)
    try:
        df = fd.read_image(
            "test_images/Photo_describeing_sample.png",
            prompt=(
                "Extract the following details: objects visible, "
                "colors, mood/atmosphere, season"
            ),
            columns=["object", "description"],
            mode="direct",
            model="openai/gpt-5-mini",
        )
        print(df)
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: English poem with direct mode (for comparison with OCR)
    print("\n3. English Poem with Direct Mode:")
    print("-" * 40)
    try:
        df = fd.read_image(
            "test_images/English_OCR_sample.png",
            prompt="Read the poem text and extract it",
            mode="direct",
            model="openai/gpt-5-mini",
        )
        print(df)
    except Exception as e:
        print(f"Error: {e}")


def compare_modes():
    """Compare OCR vs Direct mode on the same image"""
    print("\n" + "=" * 80)
    print("COMPARING OCR MODE vs DIRECT MODE")
    print("=" * 80)

    test_image = "test_images/English_OCR_sample.png"

    print("\nUsing OCR Mode:")
    print("-" * 40)
    try:
        df_ocr = fd.read_image(
            test_image, prompt="Extract the poem text", mode="ocr", language="eng"
        )
        print(df_ocr)
    except Exception as e:
        print(f"OCR Error: {e}")

    print("\nUsing Direct Mode:")
    print("-" * 40)
    try:
        df_direct = fd.read_image(
            test_image,
            prompt="Extract the poem text",
            mode="direct",
            model="openai/gpt-5-mini",
        )
        print(df_direct)
    except Exception as e:
        print(f"Direct Error: {e}")


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY environment variable is not set!")
        print("Please set it before running this example:")
        print("  export OPENROUTER_API_KEY='your-api-key-here'")
        exit(1)

    print("=" * 80)
    print("FUNDAS IMAGE READING - OCR vs DIRECT MODE EXAMPLES")
    print("=" * 80)

    # Run tests
    try:
        test_ocr_mode()
    except Exception as e:
        print(f"\nOCR Mode Tests Failed: {e}")

    try:
        test_direct_mode()
    except Exception as e:
        print(f"\nDirect Mode Tests Failed: {e}")

    try:
        compare_modes()
    except Exception as e:
        print(f"\nComparison Tests Failed: {e}")

    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
