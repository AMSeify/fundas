# Fundas Documentation

Welcome to the Fundas documentation! Fundas is an AI-powered Python library that extends pandas to extract structured data from unstructured files using the OpenRouter API.

## Quick Links

- [Getting Started](getting-started.md) - Installation and first example
- [Configuration](configuration.md) - Environment variables and settings
- [API Reference](api-reference.md) - Complete function signatures

## Reader Guides

- [PDF Reader](readers/pdf.md) - Extract data from PDF files
- [Image Reader](readers/image.md) - OCR and vision-based image analysis
- [Audio Reader](readers/audio.md) - Transcribe and extract from audio
- [Webpage Reader](readers/webpage.md) - Scrape data from web pages
- [Video Reader](readers/video.md) - Extract data from videos

## Features

- [Schema & Typed Output](schema.md) - Define output structure with types
- [Caching](caching.md) - Understand and manage API response caching

## Contributing

- [Contributing Guide](contributing.md) - How to contribute to Fundas

## What is Fundas?

Fundas makes it easy to extract structured data from various file formats by combining:

1. **File parsing** - Extracts raw content from PDFs, images, audio, video, and web pages
2. **AI extraction** - Uses LLMs via OpenRouter to intelligently structure the data
3. **DataFrame output** - Returns results as pandas DataFrames for easy analysis

### Example

```python
import fundas as fd

# Extract invoice items from a PDF
df = fd.read_pdf("invoice.pdf", prompt="Extract item name, quantity, and price")
print(df)
#   item_name  quantity  price
# 0   Widget A        10  $9.99
# 1   Widget B         5  $14.99
```

## Supported File Types

| Type | Function | Description |
|------|----------|-------------|
| PDF | `read_pdf()` | Extract text and tables from PDFs |
| Image | `read_image()` | OCR text extraction or vision analysis |
| Audio | `read_audio()` | Transcription and data extraction |
| Webpage | `read_webpage()` | Web scraping with AI extraction |
| Video | `read_video()` | Frame and audio analysis |

## License

Fundas is open source software. See [LICENSE](../LICENSE) for details.
