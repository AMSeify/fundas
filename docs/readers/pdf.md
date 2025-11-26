# PDF Reader

The `read_pdf()` function extracts structured data from PDF files using AI.

## Basic Usage

```python
import fundas as fd

df = fd.read_pdf("document.pdf", prompt="Extract all tables and data")
print(df)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `filepath` | str/Path | Required | Path to the PDF file |
| `prompt` | str | "Extract all text..." | Instructions for extraction |
| `columns` | list | None | Column names to extract |
| `schema` | Schema | None | Schema for typed output |
| `api_key` | str | None | OpenRouter API key |
| `model` | str | None | AI model to use |

## Examples

### Extract Invoice Items

```python
df = fd.read_pdf(
    "invoice.pdf",
    prompt="Extract invoice line items with product name, quantity, unit price, and total",
    columns=["product", "quantity", "unit_price", "total"]
)
```

### Extract with Schema

```python
from fundas import Schema, Column, DataType

schema = Schema([
    Column("product", DataType.STRING),
    Column("quantity", DataType.INTEGER),
    Column("price", DataType.FLOAT),
])

df = fd.read_pdf("invoice.pdf", prompt="Extract items", schema=schema)
```

### Multi-Page PDFs

The reader automatically extracts text from all pages with page breaks marked:

```python
df = fd.read_pdf("report.pdf", prompt="Extract data from all pages")
```

## How It Works

1. Text is extracted from all PDF pages using PyPDF2
2. Pages are joined with `--- Page Break ---` markers
3. Combined text is sent to the AI model
4. AI extracts structured data based on your prompt

## Tips

- Be specific in your prompt about what data to extract
- Use `columns` parameter to ensure consistent output
- Use `schema` for typed numeric/date data
- Large PDFs may need to be split for best results

## Dependencies

- `PyPDF2` - Install with: `pip install PyPDF2`

## Error Handling

```python
try:
    df = fd.read_pdf("file.pdf", prompt="Extract data")
except FileNotFoundError:
    print("PDF file not found")
except RuntimeError as e:
    print(f"Error reading PDF: {e}")
```
