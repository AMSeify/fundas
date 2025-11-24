# Fundas Examples

This directory contains example scripts demonstrating how to use Fundas to extract structured data from various file types.

## Prerequisites

Before running these examples, make sure you have:

1. **Installed Fundas**:
   ```bash
   pip install fundas
   # Or from source:
   pip install -e .
   ```

2. **Set up your API key** in one of these ways:
   - Create a `.env` file in the project root with `OPENROUTER_API_KEY=your-key`
   - Set environment variable: `export OPENROUTER_API_KEY=your-key`
   - Pass `api_key` parameter directly to functions

## Examples

### 1. PDF Structure Test (`test_pdf_structure.py`) ⭐ Start Here

**No API key required!** Tests that the PDF can be read and shows what data is available.

```bash
python examples/test_pdf_structure.py
```

**What it does:**
- Verifies the PDF file exists and can be opened
- Shows page count and extracted text length
- Demonstrates what fundas will see
- Provides example code (no actual API calls)

### 2. PDF Extraction (`test_pdf_extraction.py`)

**Requires API key!** Extract structured data from PDF documents using AI.

```bash
python examples/test_pdf_extraction.py
```

**What it demonstrates:**
- Extracting financial metrics with specific columns
- Extracting business highlights
- Extracting executive quotes
- Using different prompts for different insights

**Key patterns:**
```python
import fundas as fd

# Extract with specific columns
df = fd.read_pdf(
    "document.pdf",
    prompt="Extract quarterly revenue and expenses",
    columns=["metric", "q4_value", "q3_value", "change"]
)

# Extract with custom prompt
df = fd.read_pdf(
    "report.pdf",
    prompt="Summarize key findings from the executive summary"
)
```

### 2. Basic Usage (`usage_example.py`)

Shows the basic API for all reader functions without making actual API calls.

```bash
python examples/usage_example.py
```

## Quick Start

**New to Fundas? Start here:**

1. **Run the structure test** (no API key needed):
   ```bash
   python examples/test_pdf_structure.py
   ```

2. **Set up your API key**:
   - Get a free key from [OpenRouter](https://openrouter.ai/)
   - Add to `.env` file: `OPENROUTER_API_KEY=your-key`

3. **Try the full extraction**:
   ```bash
   python examples/test_pdf_extraction.py
   ```

## Sample Files

- **Ferguson_FY24_Q4_Press_Release.pdf**: Real-world earnings press release (14 pages, 356 KB)
  - Financial data in tabular format
  - Executive quotes and commentary
  - Business highlights and strategy
  - Perfect for testing structured data extraction
  - Contains ~34,000 characters of text

## Tips for Better Results

1. **Be specific in your prompts**: Instead of "extract data", use "extract product names, prices, and quantities"

2. **Use the columns parameter**: Helps the AI understand exactly what structure you want
   ```python
   columns=["date", "transaction", "amount", "category"]
   ```

3. **Choose the right model**: More complex documents may benefit from better models
   ```python
   model="anthropic/claude-3-opus"  # vs default gpt-3.5-turbo
   ```

4. **Check your cache**: Results are cached by default in `~/.fundas/cache/`
   ```python
   from fundas import get_cache
   cache = get_cache()
   cache.clear()  # Clear all cached results
   ```

## Common Issues

**"File not found" error:**
- Make sure you're in the correct directory or use absolute paths
- Check that the file exists: `ls -la examples/*.pdf`

**"API key required" error:**
- Verify your `.env` file has `OPENROUTER_API_KEY=...`
- Or pass `api_key="..."` parameter to functions

**Results not as expected:**
- Try a more specific prompt
- Use the `columns` parameter to guide the structure
- Consider using a more capable model
- Check the cached result in `~/.fundas/cache/` to see raw API response

## Adding Your Own Examples

1. Place your file in the `examples/` directory
2. Create a Python script that uses `fundas` to extract data
3. Add documentation to this README

## More Information

- Main README: `../README.md`
- API Documentation: See docstrings in `fundas/readers.py`
- Contributing: `../CONTRIBUTING.md`
