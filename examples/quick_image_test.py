"""
Quick test script for image reading - both OCR and Direct modes

This is a minimal example you can use to quickly test the functionality.
Make sure you have your test images ready and your API key set.
"""

import fundas as fd
import os

# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-5-mini")
if not API_KEY:
    print("ERROR: Please set OPENROUTER_API_KEY environment variable")
    print("export OPENROUTER_API_KEY='your-key-here'")
    exit(1)


print("=" * 80)
print("FUNDAS IMAGE READING - Quick Test")
print("=" * 80)

# Test 1: OCR Mode with English
print("\n1. Testing OCR Mode (English)...")
print("-" * 40)
try:
    df = fd.read_image(
        "test_images/English_OCR_sample.png",
        prompt="Extract all the text from this image",
        mode="ocr",
        language="eng",
        api_key=API_KEY,
    )
    print("✓ Success! Data extracted:")
    print(df)
except FileNotFoundError:
    print("✗ Image file not found.")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: OCR Mode with Farsi
print("\n2. Testing OCR Mode (Farsi)...")
print("-" * 40)
try:
    df = fd.read_image(
        "test_images/farsi_OCR_sample.png",
        prompt="Extract the Farsi/Persian text content",
        mode="ocr",
        language="fas",
        api_key=API_KEY,
    )
    print("✓ Success! Data extracted:")
    print(df)
except FileNotFoundError:
    print("✗ Image file not found.")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Direct Mode with Vision Model
print("\n3. Testing Direct Mode (Multimodal Model)...")
print("-" * 40)
try:
    df = fd.read_image(
        "test_images/Photo_describeing_sample.png",
        prompt="Describe this scene in detail",
        mode="direct",
        model="openai/gpt-5-mini",  # Multimodal model
        api_key=API_KEY,
    )
    print("✓ Success! Data extracted:")
    print(df)
except FileNotFoundError:
    print("✗ Image file not found.")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Direct Mode for Non-OCR Farsi (comparison)
print("\n4. Testing Direct Mode on Farsi Image (for comparison)...")
print("-" * 40)
try:
    df = fd.read_image(
        "test_images/Farsi_nonOCR_sample.png",
        prompt="Extract and describe the content of this image",
        mode="direct",
        model="openai/gpt-5-mini",
        api_key=API_KEY,
    )
    print("✓ Success! Data extracted:")
    print(df)
except FileNotFoundError:
    print("✗ Image file not found.")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 80)
print("Testing complete!")
print("=" * 80)
