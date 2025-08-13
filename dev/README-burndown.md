# 🧪 Burndown Gauntlet: Test File Generator

This directory contains scripts and resources for generating "dirty" test files packed with metadata and PII. These files are used to stress-test rMeta's detection and cleaning capabilities.

## What is this?

- **`generate_meta_dirty_files.py`** creates a bundle of files (TXT, CSV, DOCX, PDF, XLSX, JPG, etc.) with embedded metadata and sensitive information.
- The generated files are intentionally "dirty"—they contain fake names, emails, SSNs, and other data for testing.
- A zipped payload is also created for batch testing.

## How to use

1. Install the required dependencies (see script header or project requirements).
2. Run the script:
   ```bash
   python generate_meta_dirty_files.py
   ```
3. Use the generated files to test rMeta's cleaning and detection features.

## Why?

- To ensure rMeta reliably detects and removes metadata/PII from a variety of real-world file types.
- To provide a reproducible, automated way to validate privacy features during development and CI.

## Sample Dirty Files

This directory includes a set of sample "dirty" files in `generated_dirty_files_for_test/`.  
These files are intentionally packed with metadata and PII for testing rMeta’s detection and cleaning features.  
You can use them directly or regenerate them with the script in this folder.

## Note

- **Do not use real sensitive data in these files.** All PII is synthetic and for testing only.
- This directory is for development/testing only and is not included in production builds.

---

*For general project info, see [../README.md](../README.md).*