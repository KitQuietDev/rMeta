# Changelog

All notable changes to this project will be documented here.  
This format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.3.2] - 2025-08-11

### Changed
- Refactored `safeguards.py` into `system.py` for improved modularity and clarity.
- Introduced chunking logic to enhance fault tolerance during processing.  See `chunking.py` in `utils/` directory.

### Fixed
- Resolved oversight where `safeguards.py` was not properly wired into execution flow.

### Docs
- Updated README to reflect new module structure and usage.

## [0.3.1] - 2025-08-11

### Added
- Rebuilt internal workflow for github actions


## [0.3.0] - 2025-08-10

### Breaking
- **Major refactor:** This release is a near-total rewrite and is **not backward compatible** with previous versions (`0.1.x`, `0.2.x`).
- **Handler, configuration, and session logic** have all changed; any previous integrations, scripts, or automations will require updates.
- **PDF handler:** Now uses a new library for full MIT license compatibility.
- **Async/await integration:** All core logic now uses `asyncio` for improved performance and maintainability.
- **Production server:** Switched from Flask’s built-in server to Gunicorn for non-development deployments.
- **Docker Compose:** Configuration and environment variables have changed; see updated `docker-compose.yml` and `.env` for details.

### Added
- **Regex-based PII detection:** New `utils/pii_scanner.py` for scanning text for emails, SSNs, phone numbers, and more.
- **PII scanning in all major handlers:** Now integrated into `pdf_handler.py`, `docx_handler.py`, `xlsx_handler.py`, and `text_csv_handler.py`.
- **Flash messages:** UI now reports detected PII types after scrubbing, across all supported filetypes.
- **Session tracking:** Smart session tracking in `utils/cleanup.py` prevents deletion of active sessions.
- **Cleanup logic:** Integrated into `upload.py`, `download.py`, and `flask_renderer.py` for robust ephemeral file handling.
- **Development Docker Compose:** Added `docker-compose.yml.example` for local development and hot-reload support.

### Changed
- **Async execution:** Standardized use of `asyncio.to_thread()` for async-safe file and handler operations.
- **Logging:** Improved consistency and clarity of logging across all modules.
- **Docker Compose:** Restructured for production best practices and easier local development.
- **Loose ends:** Numerous bugfixes, code cleanups, and documentation improvements throughout the codebase.

---

*For migration instructions and more details, see the updated documentation and example configs.*

## [0.2.1] - 2025-07-28
### Added
- Installation experience improved — better onboarding for first-time users
- Expanded log clarity during GPG encryption steps
- Enhanced error messages for file validation and failure points

### Changed
- Reworked postprocessor naming for clarity
- Minor internal doc cleanup and README flow diagram

## [0.2.0] - 2025-07-26
### Major Updates
- Rewrote core logic with async handling
- Improved validation and error messaging across all handlers
- Added GPG encryption support
- New Docker packaging and GHCR integration

## [0.1.5] - 2025-07-22
### Initial Public Release
- Basic metadata scrubbing
- HEIC handler and rudimentary postprocessing
- Posted to Reddit and Docker Hub