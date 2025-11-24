# Contributing to Fundas

Thank you for your interest in contributing to Fundas! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors. Please be kind, considerate, and constructive in your interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/fundas.git
   cd fundas
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/AMSeify/fundas.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

3. **Install development dependencies**:
   ```bash
   pip install pytest pytest-cov black flake8
   ```

4. **Set up your OpenRouter API key** for testing (optional):
   ```bash
   export OPENROUTER_API_KEY="your-api-key-here"
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues identified in the issue tracker
- **New features**: Implement new file readers, exporters, or functionality
- **Documentation**: Improve README, docstrings, or create tutorials
- **Tests**: Add or improve test coverage
- **Performance improvements**: Optimize existing code
- **Examples**: Create example scripts or notebooks

### Finding Issues to Work On

- Check the [Issues](https://github.com/AMSeify/fundas/issues) page
- Look for issues labeled `good first issue` for beginner-friendly tasks
- Look for issues labeled `help wanted` for tasks that need contributors

### Before Starting Work

1. **Comment on the issue** you want to work on to let others know
2. **Wait for approval** from a maintainer (especially for large changes)
3. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use [Black](https://github.com/psf/black) for code formatting (line length: 88)
- Use [Flake8](https://flake8.pycqa.org/) for linting

### Code Formatting

Format your code with Black:
```bash
black fundas/ tests/
```

Check for linting issues:
```bash
flake8 fundas/ tests/ --max-line-length=88 --extend-ignore=E203
```

### Documentation

- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Type hints**: Include type hints for function parameters and return values
- **Comments**: Add comments for complex logic, but prefer self-documenting code

Example docstring:
```python
def read_pdf(
    filepath: Union[str, Path],
    prompt: str = "Extract all text and tabular data",
    api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Read a PDF file and convert it to a pandas DataFrame.
    
    Args:
        filepath: Path to the PDF file
        prompt: Description of what data to extract
        api_key: Optional OpenRouter API key
        
    Returns:
        pandas DataFrame containing extracted data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        RuntimeError: If PDF processing fails
        
    Examples:
        >>> df = read_pdf("invoice.pdf", prompt="Extract invoice items")
        >>> print(df.head())
    """
```

## Testing

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=fundas --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_core.py
```

### Writing Tests

- **Location**: Place tests in the `tests/` directory
- **Naming**: Test files should start with `test_`
- **Structure**: Use classes to group related tests
- **Mocking**: Use `unittest.mock` for mocking external dependencies (API calls, file I/O)

Example test:
```python
import pytest
from unittest.mock import Mock, patch
from fundas.readers import read_pdf

class TestReadPdf:
    @patch('fundas.readers.PdfReader')
    @patch('fundas.readers._get_client')
    def test_read_pdf_success(self, mock_client, mock_pdf):
        # Setup mocks
        mock_pdf.return_value.pages = [Mock(extract_text=Mock(return_value="test"))]
        mock_client.return_value.extract_structured_data.return_value = {"data": ["value"]}
        
        # Test
        df = read_pdf("test.pdf", api_key="test-key")
        
        # Assertions
        assert not df.empty
        assert "data" in df.columns
```

### Test Coverage

- Aim for at least 80% code coverage
- All new features should include tests
- Bug fixes should include regression tests

## Pull Request Process

### 1. Sync Your Fork

Before creating a PR, sync your fork with upstream:
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. Create Commits

- **Commit messages**: Use clear, descriptive commit messages
- **Atomic commits**: Each commit should represent a single logical change
- **Commit format**:
  ```
  Short description (50 chars or less)
  
  More detailed explanation if needed. Wrap at 72 characters.
  Explain what changed and why, not how.
  
  Fixes #123
  ```

### 3. Push Changes

```bash
git push origin feature/your-feature-name
```

### 4. Create Pull Request

1. Go to the [Fundas repository](https://github.com/AMSeify/fundas)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template:
   - **Title**: Clear, concise description
   - **Description**: Explain what changed and why
   - **Related issues**: Link to related issues (Fixes #123)
   - **Testing**: Describe how you tested the changes
   - **Screenshots**: Include if applicable

### 5. PR Review Process

- **Automated checks**: Ensure all tests and checks pass
- **Code review**: Address reviewer feedback promptly
- **Updates**: Push additional commits to the same branch
- **Merge**: Once approved, a maintainer will merge your PR

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Minimal steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, package versions
- **Code sample**: Minimal code that reproduces the issue

Example:
```markdown
## Bug Description
read_pdf fails when processing multi-page PDFs

## Steps to Reproduce
1. Install fundas
2. Run: `df = fd.read_pdf("multipage.pdf")`
3. Error occurs

## Expected Behavior
Should extract text from all pages

## Actual Behavior
RuntimeError: Page extraction failed

## Environment
- OS: Ubuntu 22.04
- Python: 3.10.8
- fundas: 0.1.0
```

### Feature Requests

When requesting features, include:

- **Description**: Clear description of the proposed feature
- **Use case**: Explain why this feature is needed
- **Examples**: Provide example usage
- **Alternatives**: Describe alternatives you've considered

## Development Workflow

### Typical Workflow

1. **Find or create an issue**
2. **Create a feature branch**
3. **Implement the change**
4. **Write/update tests**
5. **Update documentation**
6. **Format and lint code**
7. **Run tests locally**
8. **Commit changes**
9. **Push to your fork**
10. **Create a pull request**
11. **Address review feedback**
12. **Get merged!**

### Branch Naming

Use descriptive branch names:
- `feature/add-batch-processing`
- `fix/pdf-encoding-issue`
- `docs/improve-readme`
- `test/add-cache-tests`

## Questions?

If you have questions:

- Check existing [Issues](https://github.com/AMSeify/fundas/issues)
- Create a new issue with the `question` label
- Reach out to maintainers

## Thank You!

Your contributions make Fundas better for everyone. We appreciate your time and effort! 🎉
