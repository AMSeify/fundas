# Fundas AI Agent Instructions

## Project Overview
Fundas is an AI-powered Python library that extends pandas to extract structured data from unstructured files (PDFs, images, audio, video, web pages) using the OpenRouter API. All reader functions return pandas DataFrames.

## Architecture

### Core Components
- **`core.py`**: `OpenRouterClient` handles all API communication, JSON parsing from LLM responses (including markdown-wrapped JSON), and retry logic with exponential backoff
- **`readers.py`**: Five reader functions (`read_pdf`, `read_image`, `read_audio`, `read_webpage`, `read_video`) that extract file content then delegate to `OpenRouterClient.extract_structured_data()`
- **`cache.py`**: `APICache` uses SHA256 hashing of (content, prompt, model, columns) to cache API responses in `~/.fundas/cache/` with 24hr default TTL
- **`exporters.py`**: Export functions (`to_summarized_csv`, `to_summarized_excel`, `to_summarized_json`) - AI transformation is planned but not yet implemented

### Data Flow Pattern
1. Reader extracts raw content (text from PDF, OCR from image, HTML from webpage, metadata from video/audio)
2. `_get_client()` helper creates `OpenRouterClient` with default model `openai/gpt-3.5-turbo`
3. Client checks cache first, then sends prompt + content to OpenRouter API
4. Response parsing handles both plain JSON and markdown-wrapped JSON (```json blocks)
5. Parsed dict is cached and converted to pandas DataFrame

### API Integration
- All API calls require `OPENROUTER_API_KEY` environment variable or explicit `api_key` parameter
- Optional `OPENROUTER_MODEL` environment variable to set default model (fallback: `openai/gpt-3.5-turbo`)
- Use `.env` file for local configuration (auto-loaded via `python-dotenv`)
- System prompt instructs LLM: "Return data as JSON object where keys are column names and values are lists"
- Optional `columns` parameter adds: "Extract the following columns: ..." to system prompt
- Fallback: if JSON parsing fails, returns `{"content": [raw_response_text]}`

## Development Workflow

### Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Create and activate virtual environment
pip install -e .              # Install in editable mode
pip install pytest pytest-cov black flake8  # Dev dependencies

# Configure API credentials (copy from template and edit)
cp .env.example .env
# Edit .env to add your OPENROUTER_API_KEY and optionally set OPENROUTER_MODEL
```

### Testing
```bash
pytest tests/                 # Run all tests
pytest tests/ --cov=fundas --cov-report=html  # With coverage (aim for 80%+)
pytest tests/test_core.py     # Single test file
```

**Testing conventions:**
- Mock external dependencies (API calls, file I/O) using `unittest.mock`
- Test classes group related tests (e.g., `TestOpenRouterClient`, `TestReadPdf`)
- File extraction tests mock `PdfReader`, `cv2.VideoCapture`, `requests.get`, etc.
- Cache tests use temporary directories via `tmpdir` fixture

### Code Style
```bash
black fundas/ tests/          # Format (line length: 88)
flake8 fundas/ tests/ --max-line-length=88 --extend-ignore=E203
```

- **Docstrings**: Google-style with Args, Returns, Raises, Examples sections
- **Type hints**: Use `Union[str, Path]` for file paths, `Optional[str]` for nullable params
- **Imports**: Standard library → third-party → local (`.core`, `.cache`)

## Key Patterns

### Reader Function Template
All readers follow this structure:
```python
def read_X(filepath, prompt, columns=None, api_key=None, model=None):
    # 1. Validate file exists (raise FileNotFoundError)
    # 2. Extract content (text/metadata specific to file type)
    # 3. Get client via _get_client(api_key, model)
    # 4. Call client.extract_structured_data(content, prompt, columns)
    # 5. Return pd.DataFrame(data)
```

### Error Handling
- `OpenRouterClient.process_content()`: Retries 3 times with exponential backoff, raises `RuntimeError` on failure
- HTTP 400/404 errors raise `ValueError` immediately (no retry)
- File operations wrap exceptions: `PyPDF2` errors → `RuntimeError("Error reading PDF file: ...")`

### Cache Behavior
- Enabled by default (`use_cache=True` in `OpenRouterClient`)
- Cache key = SHA256 of JSON-serialized `{content, prompt, model, columns}`
- Manual cache management: `cache.clear()` removes all, `cache.clear_expired()` removes only expired
- Disable with `cache.disable()` / re-enable with `cache.enable()`

## Common Tasks

### Adding a New Reader
1. Create function in `readers.py` following template above
2. Add to `__init__.py` imports and `__all__`
3. Extract file-specific content (e.g., for Word docs: `python-docx` to extract text)
4. Write tests in `tests/test_readers.py` mocking file reading and API client
5. Add usage example to `README.md` and `examples/usage_example.py`

### Modifying API Prompts
- System prompt is in `OpenRouterClient.extract_structured_data()` line 151-154
- User prompt includes format example: `{"column1": ["value1"], ...}`
- Changes affect all readers - test thoroughly across file types

### Debugging API Responses
- Check `~/.fundas/cache/*.json` for cached responses (includes timestamp, data)
- Use `client.process_content()` directly to inspect raw API response
- Set `use_cache=False` to bypass cache during debugging

## Project-Specific Notes

- **Video/Audio Limitation**: Currently only extracts metadata, not actual transcription/OCR (noted in docstrings)
- **Image OCR**: Optional - falls back to filename if `pytesseract` not installed
- **Webpage Scraping**: Strips `<script>` and `<style>` tags, cleans whitespace
- **Excel Export**: Requires `openpyxl` (optional dependency in `pyproject.toml`)
- **Future Work**: Exporter AI transformation (warns with `FutureWarning` if `prompt` passed)

## Dependencies
Core: `pandas`, `requests`, `PyPDF2`, `Pillow`, `beautifulsoup4`, `opencv-python`, `python-dotenv`  
Dev: `pytest`, `pytest-cov`, `black`, `flake8`  
Optional: `openpyxl` (Excel), `pytesseract` (image OCR)
