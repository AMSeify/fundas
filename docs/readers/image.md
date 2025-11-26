# Image Reader

The `read_image()` function extracts structured data from images using OCR or direct vision analysis.

## Basic Usage

```python
import fundas as fd

# OCR mode (default)
df = fd.read_image("receipt.jpg", prompt="Extract items and prices")

# Direct vision mode
df = fd.read_image(
    "photo.jpg",
    prompt="Describe the scene",
    mode="direct",
    model="openai/gpt-4-vision-preview"
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | str/Path | Required | Path to the image file |
| `prompt` | str | "Describe what you see..." | Instructions for extraction |
| `columns` | list | None | Column names to extract |
| `schema` | Schema | None | Schema for typed output |
| `api_key` | str | None | OpenRouter API key |
| `model` | str | None | AI model |
| `mode` | str | "ocr" | Extraction mode: "ocr" or "direct" |
| `language` | str | "eng" | OCR language code |

## Modes

### OCR Mode (Default)

Extracts text from the image using Tesseract OCR, then sends text to the LLM:

```python
df = fd.read_image(
    "document.png",
    prompt="Extract table data",
    mode="ocr"
)
```

**Best for:** Documents, receipts, forms, scanned text

### Direct Mode

Sends the image directly to a vision-capable model:

```python
df = fd.read_image(
    "photo.jpg",
    prompt="Identify objects in the image",
    mode="direct",
    model="openai/gpt-4-vision-preview"
)
```

**Best for:** Photos, diagrams, charts, visual analysis

## Language Support

For OCR mode, specify the language:

```python
# Arabic text
df = fd.read_image("arabic.png", mode="ocr", language="ara")

# Persian/Farsi text
df = fd.read_image("persian.png", mode="ocr", language="fas")

# Spanish text
df = fd.read_image("spanish.png", mode="ocr", language="spa")
```

Common language codes:
- `eng` - English
- `ara` - Arabic
- `fas` - Persian/Farsi
- `spa` - Spanish
- `fra` - French
- `deu` - German
- `chi_sim` - Simplified Chinese
- `chi_tra` - Traditional Chinese

## Examples

### Extract Receipt Data

```python
from fundas import Schema, Column, DataType

schema = Schema([
    Column("item", DataType.STRING),
    Column("price", DataType.FLOAT),
])

df = fd.read_image(
    "receipt.jpg",
    prompt="Extract purchased items and their prices",
    schema=schema,
    mode="ocr"
)
```

### Analyze a Chart

```python
df = fd.read_image(
    "chart.png",
    prompt="Extract the data points from this bar chart",
    columns=["category", "value"],
    mode="direct",
    model="openai/gpt-4-vision-preview"
)
```

### Multi-language Document

```python
# German receipt
df = fd.read_image(
    "german_receipt.png",
    prompt="Extrahiere Artikel und Preise",  # German prompt
    mode="ocr",
    language="deu"
)
```

## Dependencies

### OCR Mode
- `Pillow` - Image handling
- `pytesseract` - OCR library
- Tesseract system package

Install tesseract:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### Direct Mode
- `Pillow` - Image handling
- Vision-capable model (e.g., `openai/gpt-4-vision-preview`)

## Error Handling

```python
try:
    df = fd.read_image("image.png", prompt="Extract data")
except FileNotFoundError:
    print("Image file not found")
except ValueError as e:
    print(f"Invalid mode: {e}")
except RuntimeError as e:
    print(f"Error processing image: {e}")
```
