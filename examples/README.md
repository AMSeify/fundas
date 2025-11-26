# Fundas Examples

This directory contains example scripts demonstrating how to use Fundas for various data extraction tasks.

## Quick Start

1. Install Fundas:
   ```bash
   pip install fundas
   ```

2. Set your OpenRouter API key:
   ```bash
   export OPENROUTER_API_KEY="your-api-key"
   ```

3. Run any example:
   ```bash
   python basic_usage.py
   ```

## Examples

### Basic Usage
- **[basic_usage.py](basic_usage.py)** - Introduction to Fundas with simple PDF extraction

### Reader Examples
- **[pdf_extraction.py](pdf_extraction.py)** - Extract data from PDF files
- **[image_analysis.py](image_analysis.py)** - OCR and vision-based image analysis
- **[audio_transcription.py](audio_transcription.py)** - Transcribe and extract data from audio
- **[webpage_scraping.py](webpage_scraping.py)** - Extract structured data from web pages

### Advanced Features
- **[schema_typed_output.py](schema_typed_output.py)** - Using Schema for typed output with data validation
- **[quick_image_test.py](quick_image_test.py)** - Quick test for image reading

## Sample Files

Sample files for testing are located in the `assets/` directory:

- **assets/Ferguson_FY24_Q4_Press_Release.pdf** - Sample PDF document
- **assets/RayayeMA.mp3** - Sample audio file (Persian)
- **assets/harvard.wav** - Sample audio file (English)
- **assets/images/** - Sample images for OCR and vision testing
  - English_OCR_sample.png
  - farsi_OCR_sample.png
  - Farsi_nonOCR_sample.png
  - Photo_describeing_sample.png

## Running with Different Models

You can specify different OpenRouter models via environment variable or parameter:

```python
# Using environment variable
import os
os.environ["OPENROUTER_MODEL"] = "anthropic/claude-3-opus"

# Or using function parameter
df = fd.read_pdf("file.pdf", model="anthropic/claude-3-opus")
```

## Troubleshooting

### API Key Issues
Make sure your `OPENROUTER_API_KEY` environment variable is set correctly.

### Missing Dependencies
For specific features, you may need additional packages:
- PDF reading: `pip install PyPDF2`
- Image OCR: `pip install pytesseract` (plus tesseract system package)
- Audio transcription: `pip install openai-whisper`
- Video processing: `pip install opencv-python`
