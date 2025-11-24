#!/usr/bin/env python
"""
Simple PDF structure test - verify PDF can be read and parsed

This script tests that the PDF file exists and can be opened,
without making actual API calls.
"""

import sys
from pathlib import Path

def test_pdf_structure():
    """Test that the PDF can be accessed and read."""
    print("=" * 70)
    print("PDF Structure Test (No API Calls)")
    print("=" * 70)
    print()
    
    # Path to the PDF file
    pdf_path = Path(__file__).parent / "Ferguson_FY24_Q4_Press_Release.pdf"
    
    # Test 1: File exists
    print("Test 1: File exists")
    if pdf_path.exists():
        print(f"✓ PDF found: {pdf_path.name}")
        print(f"  Size: {pdf_path.stat().st_size / 1024:.1f} KB")
    else:
        print(f"✗ PDF not found at {pdf_path}")
        return False
    print()
    
    # Test 2: Can read with PyPDF2
    print("Test 2: Can read with PyPDF2")
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        num_pages = len(reader.pages)
        print(f"✓ PDF opened successfully")
        print(f"  Pages: {num_pages}")
        
        # Extract first page text as sample
        first_page_text = reader.pages[0].extract_text()
        print(f"  First page text length: {len(first_page_text)} characters")
        print(f"  Sample: {first_page_text[:100]}...")
    except Exception as e:
        print(f"✗ Failed to read PDF: {e}")
        return False
    print()
    
    # Test 3: Show what fundas would see
    print("Test 3: Content preview (what fundas sees)")
    try:
        text_content = []
        for i, page in enumerate(reader.pages):
            text_content.append(page.extract_text())
        
        full_text = "\n\n--- Page Break ---\n\n".join(text_content)
        print(f"✓ Extracted text from all {num_pages} pages")
        print(f"  Total length: {len(full_text)} characters")
        print(f"  First 200 chars: {full_text[:200]}...")
    except Exception as e:
        print(f"✗ Failed to extract text: {e}")
        return False
    print()
    
    # Test 4: Show example usage (without API call)
    print("Test 4: Example fundas usage (documentation)")
    print("-" * 70)
    print("To extract data from this PDF with fundas:")
    print()
    print("  import fundas as fd")
    print()
    print("  # Extract financial metrics")
    print("  df = fd.read_pdf(")
    print(f'      "{pdf_path.name}",')
    print('      prompt="Extract Q4 revenue, net income, and EPS",')
    print('      columns=["metric", "value"]')
    print("  )")
    print()
    print("Requirements:")
    print("  - Valid OPENROUTER_API_KEY in .env file")
    print("  - Active internet connection")
    print("  - OpenRouter API credits")
    print()
    
    print("=" * 70)
    print("✓ All structure tests passed!")
    print("  The PDF is ready for fundas processing")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = test_pdf_structure()
    sys.exit(0 if success else 1)
