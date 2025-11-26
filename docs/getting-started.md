# Getting Started with Fundas

This guide will help you install Fundas and run your first data extraction.

## Prerequisites

- Python 3.8+
- An OpenRouter API key ([Get one here](https://openrouter.ai/))

## Installation

Install Fundas using pip:

```bash
pip install fundas
```

### Optional Dependencies

Depending on your use case, you may need additional packages:

```bash
# For PDF reading
pip install PyPDF2

# For image OCR (also requires tesseract system package)
pip install pytesseract Pillow

# For local audio transcription
pip install openai-whisper

# For video processing
pip install opencv-python

# For Excel export
pip install openpyxl
```

## API Key Setup

Fundas requires an OpenRouter API key. Set it as an environment variable:

```bash
export OPENROUTER_API_KEY="your-api-key"
```

Or in Python:

```python
import os
os.environ["OPENROUTER_API_KEY"] = "your-api-key"
```

Or pass it directly to functions:

```python
df = fd.read_pdf("file.pdf", api_key="your-api-key")
```

For local development, create a `.env` file in your project:

```
OPENROUTER_API_KEY=your-api-key
OPENROUTER_MODEL=openai/gpt-3.5-turbo  # Optional: set default model
```

## Your First Extraction

### Basic Example

```python
import fundas as fd

# Extract data from a PDF
df = fd.read_pdf(
    "invoice.pdf",
    prompt="Extract invoice items with name, quantity, and price"
)
print(df)
```

### With Column Specification

```python
df = fd.read_pdf(
    "report.pdf",
    prompt="Extract financial data",
    columns=["date", "metric", "value"]
)
```

### With Schema for Typed Output

```python
from fundas import Schema, Column, DataType

schema = Schema([
    Column("item", DataType.STRING, description="Product name"),
    Column("price", DataType.FLOAT, description="Price in USD"),
    Column("quantity", DataType.INTEGER),
])

df = fd.read_pdf("invoice.pdf", prompt="Extract items", schema=schema)
# DataFrame will have proper numeric types
```

## Reader Functions

Fundas provides several reader functions for different file types:

| Function | Description |
|----------|-------------|
| `read_pdf()` | Extract from PDF files |
| `read_image()` | Extract from images (OCR or vision) |
| `read_audio()` | Extract from audio files |
| `read_webpage()` | Extract from web pages |
| `read_video()` | Extract from video files |

## Common Parameters

All reader functions share these parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | str | Instructions for what data to extract |
| `columns` | list | Optional column names to extract |
| `schema` | Schema | Optional schema for typed output |
| `api_key` | str | OpenRouter API key |
| `model` | str | AI model to use |

## Next Steps

- [Configuration](configuration.md) - Learn about all configuration options
- [Schema](schema.md) - Define typed schemas for structured output
- [API Reference](api-reference.md) - Complete function documentation
