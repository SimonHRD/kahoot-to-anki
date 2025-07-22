# Changelog
## [1.2.1] - 2025-07-22
### Fixed
- Crash when input contains special characters like `<`, `&`, or `"` by HTML-escaping all string values

## [1.2.0] - 2025-07-17
### Added
- `--version` CLI flag
- Unit tests for CLI and processing modules
- CHANGELOG.md

### Fixed
- Crash when answers contain numbers (string conversion)
- Crash when processing empty Excel files

## [1.1.0] – 2025‑07‑16
- Added `--sheet` CLI argument
- Refactored into `cli.py`, `processing.py`, `main.py`

## [1.0.0] – 2025‑07‑16
- Initial release with core functionality & Docker and pip support