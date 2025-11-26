# API Reference

Complete reference for all Fundas functions and classes.

## Reader Functions

### read_pdf

```python
fundas.read_pdf(
    filepath: Union[str, Path],
    prompt: str = "Extract all text and tabular data from this PDF",
    columns: Optional[List[str]] = None,
    schema: Optional[Schema] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> pd.DataFrame
```

Extract structured data from a PDF file.

**Parameters:**
- `filepath`: Path to the PDF file
- `prompt`: Instructions for what data to extract
- `columns`: Optional list of column names
- `schema`: Optional Schema for typed output
- `api_key`: OpenRouter API key
- `model`: AI model to use

**Returns:** pandas DataFrame

---

### read_image

```python
fundas.read_image(
    filepath: Union[str, Path],
    prompt: str = "Describe what you see in this image and extract any text or data",
    columns: Optional[List[str]] = None,
    schema: Optional[Schema] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    mode: str = "ocr",
    language: str = "eng",
) -> pd.DataFrame
```

Extract structured data from an image file.

**Parameters:**
- `filepath`: Path to the image file
- `prompt`: Instructions for extraction
- `columns`: Optional column names
- `schema`: Optional Schema for typed output
- `api_key`: OpenRouter API key
- `model`: AI model (use vision model for `mode="direct"`)
- `mode`: `"ocr"` (text extraction) or `"direct"` (vision)
- `language`: Tesseract language code for OCR

**Returns:** pandas DataFrame

---

### read_audio

```python
fundas.read_audio(
    filepath: Union[str, Path],
    prompt: str = "Transcribe this audio and extract key information",
    columns: Optional[List[str]] = None,
    schema: Optional[Schema] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    language: Optional[str] = None,
    whisper_model: str = "base",
    device: Optional[str] = None,
    use_openrouter: bool = False,
) -> pd.DataFrame
```

Extract structured data from an audio file.

**Parameters:**
- `filepath`: Path to the audio file
- `prompt`: Instructions for extraction
- `columns`: Optional column names
- `schema`: Optional Schema for typed output
- `api_key`: OpenRouter API key
- `model`: AI model
- `language`: Language code (ISO for Whisper, full name for OpenRouter)
- `whisper_model`: Whisper model size
- `device`: `"cpu"` or `"cuda"`
- `use_openrouter`: Send audio directly to OpenRouter

**Returns:** pandas DataFrame

---

### read_webpage

```python
fundas.read_webpage(
    url: str,
    prompt: str = "Extract main content and data from this webpage",
    columns: Optional[List[str]] = None,
    schema: Optional[Schema] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    headers: Optional[dict] = None,
    cookies: Optional[dict] = None,
    proxy: Optional[str] = None,
    payload: Optional[dict] = None,
    method: str = "GET",
    timeout: int = 30,
    verify_ssl: bool = True,
    follow_redirects: bool = True,
    max_redirects: int = 10,
    encoding: Optional[str] = None,
    auth: Optional[tuple] = None,
    retry_count: int = 3,
    retry_delay: float = 1.0,
) -> pd.DataFrame
```

Extract structured data from a webpage.

**Parameters:**
- `url`: URL of the webpage
- `prompt`: Instructions for extraction
- `columns`: Optional column names
- `schema`: Optional Schema for typed output
- `api_key`: OpenRouter API key
- `model`: AI model
- `headers`: Custom HTTP headers
- `cookies`: Cookies to send
- `proxy`: Proxy URL
- `payload`: POST/PUT request body
- `method`: HTTP method
- `timeout`: Request timeout in seconds
- `verify_ssl`: Verify SSL certificates
- `follow_redirects`: Follow HTTP redirects
- `max_redirects`: Maximum redirects
- `encoding`: Force response encoding
- `auth`: (username, password) tuple
- `retry_count`: Number of retries
- `retry_delay`: Delay between retries

**Returns:** pandas DataFrame

---

### read_video

```python
fundas.read_video(
    filepath: Union[str, Path],
    prompt: str = "Analyze this video and extract key information",
    from_: Union[str, List[str]] = "both",
    columns: Optional[List[str]] = None,
    schema: Optional[Schema] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    sample_rate: int = 30,
) -> pd.DataFrame
```

Extract structured data from a video file.

**Parameters:**
- `filepath`: Path to the video file
- `prompt`: Instructions for extraction
- `from_`: Source to extract from: `"pics"`, `"audios"`, or `"both"`
- `columns`: Optional column names
- `schema`: Optional Schema for typed output
- `api_key`: OpenRouter API key
- `model`: AI model
- `sample_rate`: Extract 1 frame per N frames

**Returns:** pandas DataFrame

---

## Exporter Functions

### to_summarized_csv

```python
fundas.to_summarized_csv(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> None
```

Export DataFrame to CSV. AI transformation is planned for future release.

---

### to_summarized_excel

```python
fundas.to_summarized_excel(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    prompt: Optional[str] = None,
    sheet_name: str = "Sheet1",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> None
```

Export DataFrame to Excel. AI transformation is planned for future release.

---

### to_summarized_json

```python
fundas.to_summarized_json(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    orient: str = "records",
    **kwargs
) -> None
```

Export DataFrame to JSON. AI transformation is planned for future release.

---

### summarize_dataframe

```python
fundas.summarize_dataframe(
    df: pd.DataFrame,
    prompt: str = "Provide a summary of this data",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> str
```

Generate an AI-powered summary of a DataFrame.

**Returns:** AI-generated summary string

---

## Classes

### OpenRouterClient

```python
fundas.OpenRouterClient(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    use_cache: bool = True,
    cache_ttl: int = 86400,
    max_retries: int = 3,
    retry_delay: int = 1,
)
```

Client for interacting with OpenRouter API.

**Methods:**
- `process_content(content, prompt, system_prompt, response_format)` - Send content for processing
- `extract_structured_data(content, prompt, columns)` - Extract structured data
- `extract_structured_data_with_schema(content, prompt, schema)` - Extract with schema
- `extract_structured_data_from_image(image_base64, prompt, columns)` - Extract from image
- `extract_structured_data_from_audio(filepath, prompt, columns, language)` - Extract from audio

---

### APICache

```python
fundas.APICache(
    cache_dir: Optional[str] = None,
    ttl: int = 86400,
)
```

Cache for API responses.

**Methods:**
- `get(content, prompt, model, columns)` - Get cached data
- `set(content, prompt, model, data, columns)` - Cache data
- `clear()` - Clear all entries
- `clear_expired()` - Clear expired entries
- `enable()` - Enable caching
- `disable()` - Disable caching

---

### Schema

```python
fundas.Schema(
    columns: Union[List[Column], Dict[str, Union[str, DataType]]],
    name: str = "extracted_data",
    strict: bool = True,
)
```

Define output structure with typed columns.

**Methods:**
- `get_column_names()` - Get list of column names
- `get_column(name)` - Get Column by name
- `to_json_schema()` - Convert to JSON Schema
- `to_response_format()` - Format for API
- `convert_data(data)` - Convert values to proper types

---

### Column

```python
fundas.Column(
    name: str,
    dtype: Union[DataType, str],
    description: Optional[str] = None,
    required: bool = True,
    nullable: bool = False,
    enum_values: Optional[List[Any]] = None,
    date_format: Optional[str] = None,
    array_item_type: Optional[Union[DataType, str]] = None,
    default: Optional[Any] = None,
)
```

Define a column with specific data type.

**Methods:**
- `to_json_schema()` - Convert to JSON Schema
- `convert_value(value)` - Convert value to appropriate type

---

### DataType

Enum of supported data types:

- `DataType.STRING`
- `DataType.INTEGER`
- `DataType.FLOAT`
- `DataType.BOOLEAN`
- `DataType.DATE`
- `DataType.DATETIME`
- `DataType.JSON`
- `DataType.ARRAY`
