#!/usr/bin/env python
"""
Quick test script to verify the setup works.
Run this with: python test_setup.py
"""

import os
import sys


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        import fundas

        assert fundas
        print("✓ fundas imported successfully")

        import pandas

        assert pandas
        print("✓ pandas imported")

        import requests

        assert requests
        print("✓ requests imported")

        from PyPDF2 import PdfReader

        assert PdfReader
        print("✓ PyPDF2 imported")

        from PIL import Image

        assert Image
        print("✓ Pillow imported")

        from bs4 import BeautifulSoup

        assert BeautifulSoup
        print("✓ beautifulsoup4 imported")

        import cv2

        assert cv2
        print("✓ opencv-python imported")

        from dotenv import load_dotenv

        assert load_dotenv
        print("✓ python-dotenv imported")

        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_env_loading():
    """Test that environment variables are loaded."""
    print("\nTesting environment configuration...")
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL")

    if api_key:
        print(f"✓ OPENROUTER_API_KEY is set (length: {len(api_key)})")
    else:
        print("⚠ OPENROUTER_API_KEY is not set")
        print("  Edit .env file and add your API key")

    if model:
        print(f"✓ OPENROUTER_MODEL is set: {model}")
    else:
        print("ℹ OPENROUTER_MODEL not set (will use default: " "openai/gpt-3.5-turbo)")

    return api_key is not None


def test_client_creation():
    """Test creating OpenRouterClient."""
    print("\nTesting client creation...")
    try:
        from fundas.core import OpenRouterClient

        # Test with mock API key if real one not available
        api_key = os.environ.get("OPENROUTER_API_KEY", "test-key-for-init")
        client = OpenRouterClient(api_key=api_key)

        print("✓ OpenRouterClient created successfully")
        print(f"  Model: {client.model}")
        print(f"  Cache enabled: {client.use_cache}")

        return True
    except Exception as e:
        print(f"✗ Client creation failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Fundas Setup Test")
    print("=" * 60)

    results = []
    results.append(test_imports())
    results.append(test_env_loading())
    results.append(test_client_creation())

    print("\n" + "=" * 60)
    if all(results):
        print("✓ All tests passed! Setup is complete.")
        if not os.environ.get("OPENROUTER_API_KEY"):
            print("\nNote: Add your OPENROUTER_API_KEY to .env to use the " "library")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
