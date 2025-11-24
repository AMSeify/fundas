#!/usr/bin/env python
"""
Example: Extract data from a PDF file using Fundas

This example demonstrates how to use fundas to extract structured data
from the Ferguson Q4 FY24 earnings press release PDF.
"""

import fundas as fd
import pandas as pd
from pathlib import Path

def main():
    print("=" * 70)
    print("Fundas PDF Extraction Example")
    print("=" * 70)
    print()
    
    # Path to the PDF file
    pdf_path = Path(__file__).parent / "Ferguson_FY24_Q4_Press_Release.pdf"
    
    if not pdf_path.exists():
        print(f"❌ Error: PDF file not found at {pdf_path}")
        print("   Please ensure the PDF is in the examples folder.")
        return
    
    print(f"📄 Reading PDF: {pdf_path.name}")
    print()
    
    # Example 1: Extract key financial metrics
    print("Example 1: Extract Financial Metrics")
    print("-" * 70)
    try:
        df_financials = fd.read_pdf(
            pdf_path,
            prompt="Extract quarterly financial metrics including revenue, operating income, and earnings per share for Q4 2024",
            columns=["metric", "q4_2024", "q4_2023", "change_percent"]
        )
        print(df_financials.to_string(index=False))
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # Example 2: Extract company highlights
    print("\nExample 2: Extract Business Highlights")
    print("-" * 70)
    try:
        df_highlights = fd.read_pdf(
            pdf_path,
            prompt="Extract key business highlights and achievements mentioned in the press release",
            columns=["category", "highlight"]
        )
        print(df_highlights.to_string(index=False))
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # Example 3: General extraction with custom prompt
    print("\nExample 3: Extract Executive Quotes")
    print("-" * 70)
    try:
        df_quotes = fd.read_pdf(
            pdf_path,
            prompt="Extract executive quotes with the speaker's name and their statement"
        )
        print(df_quotes.to_string(index=False))
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    # Example 4: Using different AI models
    print("\nExample 4: Extract with Different Model")
    print("-" * 70)
    print("(Using model from .env or default)")
    try:
        df_summary = fd.read_pdf(
            pdf_path,
            prompt="Provide a brief summary of the company's performance in Q4 2024"
        )
        print(df_summary.to_string(index=False))
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
    
    print("=" * 70)
    print("✅ Examples complete!")
    print()
    print("Note: Results depend on:")
    print("  - Your OPENROUTER_API_KEY in .env file")
    print("  - The AI model specified (OPENROUTER_MODEL in .env)")
    print("  - The quality of the prompt")
    print("=" * 70)

if __name__ == "__main__":
    main()
