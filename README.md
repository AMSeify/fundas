# Fundas

**Fun**damental **Da**ta **S**ource - An AI-powered Python library that extends pandas to import and analyze complex, unstructured files.

## Overview

Fundas leverages the OpenRouter API and generative AI to intelligently extract features and structured data from various file types based on simple prompts. It seamlessly converts any file into a clean pandas DataFrame for immediate analysis.

## Features

- 📄 **`read_pdf()`** - Extract structured data from PDF documents
- 🖼️ **`read_image()`** - Extract data and text from images
- 🎵 **`read_audio()`** - Process audio files and extract information
- 🌐 **`read_webpage()`** - Scrape and structure web content
- 🎥 **`read_video()`** - Analyze video content from frames, audio, or both

All functions return pandas DataFrames, making the data ready for immediate analysis!

## Installation

```bash
pip install fundas
```

Or install from source:

```bash
git clone https://github.com/AMSeify/fundas.git
cd fundas
pip install -e .
```

## Quick Start

### Setup

First, set your OpenRouter API key:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Or pass it directly to the functions:

```python
import fundas as fd

df = fd.read_pdf("document.pdf", api_key="your-api-key-here")
```

### Basic Usage

#### Read PDF Files

```python
import fundas as fd

# Extract invoice data
df = fd.read_pdf(
    "invoice.pdf",
    prompt="Extract invoice items with product name, quantity, and price"
)
print(df)
```

#### Read Images

```python
# Extract data from a chart or screenshot
df = fd.read_image(
    "sales_chart.png",
    prompt="Extract the sales data points from this chart"
)
print(df)

# Process a receipt
df = fd.read_image(
    "receipt.jpg",
    prompt="Extract items and their prices",
    columns=["item", "price", "quantity"]
)
```

#### Read Webpages

```python
# Scrape product information
df = fd.read_webpage(
    "https://example.com/products",
    prompt="Extract product names, descriptions, and prices"
)
print(df)

# Extract article data
df = fd.read_webpage(
    "https://news.example.com/article",
    columns=["title", "author", "date", "content"]
)
```

#### Read Audio Files

```python
# Transcribe and extract meeting notes
df = fd.read_audio(
    "meeting.mp3",
    prompt="Extract speaker names and key discussion points"
)
```

#### Read Video Files

```python
# Analyze video frames
df = fd.read_video(
    "presentation.mp4",
    prompt="Extract slide titles and key points from this presentation",
    from_="pics"  # Extract from video frames
)

# Process audio track
df = fd.read_video(
    "lecture.mp4",
    prompt="Transcribe the lecture and identify key topics",
    from_="audios"  # Extract from audio track
)

# Analyze both video and audio
df = fd.read_video(
    "interview.mp4",
    prompt="Extract interview questions and answers",
    from_="both"  # or from_=["pics", "audios"]
)
```

## Advanced Usage

### Specify Columns

You can specify which columns you want to extract:

```python
df = fd.read_pdf(
    "report.pdf",
    prompt="Extract quarterly financial data",
    columns=["quarter", "revenue", "expenses", "profit"]
)
```

### Custom AI Models

Use different AI models via OpenRouter:

```python
df = fd.read_image(
    "complex_diagram.png",
    prompt="Extract relationships between components",
    model="anthropic/claude-3-opus"
)
```

### DataFrame Operations

Since all functions return pandas DataFrames, you can immediately use pandas operations:

```python
import fundas as fd

# Read and analyze in one workflow
df = fd.read_pdf("sales.pdf", prompt="Extract sales data")
print(df.head())
print(df.describe())
print(df.groupby('region')['sales'].sum())
```

## Requirements

- Python >= 3.8
- pandas >= 1.3.0
- requests >= 2.25.0
- PyPDF2 >= 3.0.0
- Pillow >= 10.3.0
- beautifulsoup4 >= 4.9.0
- opencv-python >= 4.8.1.78

## Advanced Features

### Caching

Fundas includes an intelligent caching system to reduce redundant API calls:

```python
import fundas as fd

# Enable caching (enabled by default)
df = fd.read_pdf("document.pdf", prompt="Extract data")

# The same file with the same prompt will use cached results
df2 = fd.read_pdf("document.pdf", prompt="Extract data")  # No API call

# Disable caching if needed
from fundas import OpenRouterClient
client = OpenRouterClient(api_key="key", use_cache=False)
```

### Exporting Data

Export your DataFrames with AI-powered summarization:

```python
import fundas as fd
import pandas as pd

# Create a DataFrame
df = pd.DataFrame({"product": ["A", "B", "C"], "sales": [100, 200, 150]})

# Export to CSV
fd.to_summarized_csv(df, "output.csv")

# Export to Excel with AI summary
fd.to_summarized_excel(
    df,
    "summary.xlsx",
    prompt="Add a summary row with totals"
)

# Generate AI summary
summary = fd.summarize_dataframe(df, prompt="Summarize sales performance")
print(summary)
```

### Error Handling

Fundas includes robust error handling with automatic retries:

```python
import fundas as fd

try:
    df = fd.read_pdf("document.pdf", prompt="Extract data")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
```

### Cache Management

Control the cache behavior:

```python
from fundas import get_cache

cache = get_cache()

# Clear all cache entries
cache.clear()

# Clear only expired entries
cache.clear_expired()

# Disable/enable cache
cache.disable()
cache.enable()
```

## API Reference

### Read Functions

All read functions share similar parameters:

**Common Parameters:**
- `filepath` or `url` (str | Path): Source file or URL
- `prompt` (str): Description of what data to extract
- `columns` (List[str], optional): Column names to extract
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use (default: gpt-3.5-turbo)

**Returns:** pandas DataFrame

### Export Functions

All export functions accept:

**Parameters:**
- `df` (pd.DataFrame): DataFrame to export
- `filepath` (str | Path): Output file path
- `prompt` (str, optional): AI transformation prompt
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use

### `read_pdf(filepath, prompt, columns=None, api_key=None, model=None)`

Extract structured data from PDF files.

**Parameters:**
- `filepath` (str | Path): Path to the PDF file
- `prompt` (str): Description of what data to extract
- `columns` (List[str], optional): Column names to extract
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use

**Returns:** pandas DataFrame

### `read_image(filepath, prompt, columns=None, api_key=None, model=None)`

Extract structured data from image files.

**Parameters:**
- `filepath` (str | Path): Path to the image file
- `prompt` (str): Description of what data to extract
- `columns` (List[str], optional): Column names to extract
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use

**Returns:** pandas DataFrame

### `read_audio(filepath, prompt, columns=None, api_key=None, model=None)`

Extract structured data from audio files.

**Parameters:**
- `filepath` (str | Path): Path to the audio file
- `prompt` (str): Description of what data to extract
- `columns` (List[str], optional): Column names to extract
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use

**Returns:** pandas DataFrame

### `read_webpage(url, prompt, columns=None, api_key=None, model=None)`

Extract structured data from web pages.

**Parameters:**
- `url` (str): URL of the webpage
- `prompt` (str): Description of what data to extract
- `columns` (List[str], optional): Column names to extract
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use

**Returns:** pandas DataFrame

### `read_video(filepath, prompt, from_='both', columns=None, api_key=None, model=None, sample_rate=30)`

Extract structured data from video files.

**Parameters:**
- `filepath` (str | Path): Path to the video file
- `prompt` (str): Description of what data to extract
- `from_` (str | List[str]): Source to extract from - 'pics', 'audios', or 'both'
- `columns` (List[str], optional): Column names to extract
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use
- `sample_rate` (int): Frame sampling rate (default: 30)

**Returns:** pandas DataFrame

### `to_summarized_csv(df, filepath, prompt=None, api_key=None, model=None, **kwargs)`

Export DataFrame to CSV with optional AI-powered summarization.

**Parameters:**
- `df` (pd.DataFrame): DataFrame to export
- `filepath` (str | Path): Path to save the CSV file
- `prompt` (str, optional): Prompt to transform/summarize data
- `api_key` (str, optional): OpenRouter API key
- `model` (str, optional): AI model to use
- `**kwargs`: Additional arguments for `pd.DataFrame.to_csv()`

### `to_summarized_excel(df, filepath, prompt=None, sheet_name="Sheet1", api_key=None, model=None, **kwargs)`

Export DataFrame to Excel with optional AI-powered summarization.

### `to_summarized_json(df, filepath, prompt=None, api_key=None, model=None, orient="records", **kwargs)`

Export DataFrame to JSON with optional AI-powered summarization.

### `summarize_dataframe(df, prompt="Provide a summary of this data", api_key=None, model=None)`

Generate an AI-powered summary of a DataFrame.

**Returns:** str (AI-generated summary)

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key

### Cache Settings

The cache is stored in `~/.fundas/cache/` by default. You can configure:
- Cache directory location
- Time-to-live (TTL) for cache entries
- Enable/disable caching

## Performance Tips

1. **Use caching**: Keep caching enabled (default) to avoid redundant API calls
2. **Specify columns**: When you know what columns you need, specify them explicitly
3. **Choose the right model**: Balance speed, cost, and accuracy by selecting appropriate models
4. **Batch operations**: Process multiple files in sequence to leverage cache warming

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! We appreciate bug fixes, new features, documentation improvements, and more.

Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Setting up your development environment
- Coding standards and style guide
- Testing requirements
- Pull request process

Quick start:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Support

For issues and questions, please open an issue on [GitHub](https://github.com/AMSeify/fundas/issues).
