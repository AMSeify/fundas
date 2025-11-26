# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-11-26

### Added

- **Image reading with OCR and direct vision modes** - `read_image()` function now supports two extraction modes:
  - `mode="ocr"` (default): Extracts text from images using OCR (pytesseract) then sends to LLM for structured data extraction
  - `mode="direct"`: Sends images directly to vision-capable LLMs (e.g., GPT-4 Vision) for analysis
- Multi-language OCR support via the `language` parameter (e.g., "eng", "ara", "fas", "spa")

### Changed

- Package name reverted from `fundas-ai` back to `fundas` for consistency
- Updated installation command in documentation to use `fundas`
- Improved formatting of prompts and documentation in `read_image` function

### Fixed

- Fixed line length issues in docstrings and prompts to comply with flake8 (max 88 characters)
- Removed unused `base64` import from `core.py`
- Removed duplicate `process_content` method definition in `OpenRouterClient`

## [0.1.0] - 2025-11-24

### Added

- Initial release of Fundas
- Core `OpenRouterClient` for API communication with OpenRouter
- `read_pdf()` - Extract structured data from PDF files
- `read_image()` - Extract data from images (basic OCR support)
- `read_audio()` - Extract metadata from audio files
- `read_video()` - Extract metadata and frame information from video files
- `read_webpage()` - Scrape and extract data from web pages
- API response caching with configurable TTL (default: 24 hours)
- Export functions: `to_summarized_csv`, `to_summarized_excel`, `to_summarized_json`
- Comprehensive test suite with pytest
- Full documentation and usage examples

[Unreleased]: https://github.com/AMSeify/fundas/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/AMSeify/fundas/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/AMSeify/fundas/releases/tag/v0.1.0
