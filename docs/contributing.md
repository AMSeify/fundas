# Contributing to Fundas

Thank you for your interest in contributing to Fundas! This document provides guidelines for contributing.

## Getting Started

### Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/fundas.git
   cd fundas
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Configure API key for testing:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=fundas --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestOpenRouterClient::test_init_with_api_key
```

### Code Formatting

```bash
# Format code with black
black src/fundas/ tests/

# Check linting with flake8
flake8 src/fundas/ tests/ --max-line-length=88 --extend-ignore=E203
```

### Pre-commit Checks

Before committing, ensure:
1. All tests pass
2. Code is formatted with black
3. No linting errors

## Project Structure

```
fundas/
├── src/fundas/         # Source code
│   ├── __init__.py     # Public API exports
│   ├── client.py       # OpenRouterClient
│   ├── cache.py        # API caching
│   ├── schema.py       # Schema classes
│   ├── readers/        # Reader functions
│   ├── exporters/      # Export functions
│   └── utils/          # Utilities
├── tests/              # Test files
├── docs/               # Documentation
└── examples/           # Example scripts
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 with 88 character line length (black default)
- Use type hints for function signatures
- Write Google-style docstrings
- Keep functions focused and small

### Docstring Format

```python
def function_name(param1: str, param2: int = 0) -> str:
    """
    Short description of the function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid

    Examples:
        >>> function_name("test", 5)
        "result"
    """
```

### Testing

- Write tests for new features
- Maintain test coverage above 80%
- Mock external dependencies (API calls, file I/O)
- Use pytest fixtures for common setup

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new read_excel function`
- `fix: Handle empty PDF pages`
- `docs: Update API reference`
- `test: Add tests for schema validation`
- `refactor: Extract JSON parsing to utils`

## Adding New Features

### Adding a New Reader

1. Create `src/fundas/readers/newtype.py`:
   ```python
   from .base import _get_client, _extract_data, _apply_schema_dtypes

   def read_newtype(filepath, prompt="...", columns=None, schema=None, ...):
       # 1. Validate file exists
       # 2. Extract content
       # 3. Get client
       # 4. Extract structured data
       # 5. Return DataFrame
   ```

2. Add to `src/fundas/readers/__init__.py`

3. Add to `src/fundas/__init__.py`

4. Add tests in `tests/readers/test_newtype.py`

5. Add documentation in `docs/readers/newtype.md`

### Modifying API Behavior

- Ensure backward compatibility
- Update documentation
- Add/update tests
- Consider impact on caching

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and commit

3. Push and create PR:
   ```bash
   git push origin feature/my-feature
   ```

4. Ensure CI passes

5. Request review

## Questions?

- Open an issue for bugs or feature requests
- Discuss in PR comments
- Check existing issues and PRs first

Thank you for contributing!
