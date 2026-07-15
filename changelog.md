# Changelog

All notable changes to this project will be documented here.
This format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.4.0] - 2025-08-15

### Added
- Session isolation: the upload route now purges stale data only when new files are detected.
- Directory watchdog (10s interval) that monitors upload state and triggers UI updates.
- Hostile payload generator (`meta_dirty_bundle`) for synthetic PII testing across supported formats.
- GitLab CI pipeline for DockerHub and GHCR image publishing.

### Changed
- UI cleanup button now reflects directory state without requiring user interaction.
- CI/CD moved to GitLab; GitHub remains active but is no longer used for publishing.
- UI layout switched from a linear list to tables for clarity.

### Fixed
- Read-only file handling in the scrubber; metadata removal no longer errors on read-only inputs.
- Mixed batch upload handling; working directory now stays consistent across a session.

## [0.3.2] - 2025-08-11

### Changed
- Refactored `safeguards.py` into `system.py` for clarity.
- Added chunking logic (`utils/chunking.py`) so large batches degrade gracefully instead of failing outright.

### Fixed
- `safeguards.py` wasn't actually wired into the execution flow — fixed.

### Docs
- Updated README to match the new module structure.

## [0.3.1] - 2025-08-11

### Added
- Rebuilt GitHub Actions workflow.

## [0.3.0] - 2025-08-10

Near-total rewrite. **Not backward compatible** with `0.1.x` or `0.2.x` — handler, configuration, and session logic all changed.

### Added
- `utils/pii_scanner.py` — regex-based detection for emails, SSNs, phone numbers, and more.
- PII scanning wired into `pdf_handler.py`, `docx_handler.py`, `xlsx_handler.py`, and `text_csv_handler.py`.
- UI now reports detected PII types after scrubbing.
- Session tracking in `utils/cleanup.py` to avoid deleting active sessions.
- `docker-compose.yml.example` for local development with hot reload.

### Changed
- PDF handler switched to a library with full MIT license compatibility.
- Core logic moved to `asyncio` throughout, standardized on `asyncio.to_thread()` for file and handler operations.
- Production serving switched from Flask's dev server to Gunicorn.
- `docker-compose.yml` restructured for production use; `.env` variables changed accordingly.
- Cleanup logic integrated into `upload.py`, `download.py`, and `flask_renderer.py`.

## [0.2.1] - 2025-07-28

### Added
- Smoother first-run onboarding.
- Clearer logging during GPG encryption.
- Better error messages for file validation failures.

### Changed
- Renamed postprocessors for clarity.
- Minor doc cleanup and README flow diagram.

## [0.2.0] - 2025-07-26

- Rewrote core logic around async handling.
- Improved validation and error messages across all handlers.
- Added GPG encryption support.
- New Docker packaging and GHCR integration.

## [0.1.5] - 2025-07-22

### Initial public release
- Basic metadata scrubbing.
- HEIC handler and rudimentary postprocessing.
