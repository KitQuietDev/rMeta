# Developer notes

Notes for anyone extending or maintaining rMeta.

## Project layout

```
.
├── app.py                    # Flask app entry point
├── handlers/                 # File-type-specific metadata scrubbers
├── postprocessors/           # Optional extras: GPG, hashing
├── static/                   # CSS and JS
├── templates/                # HTML templates (currently just index.html)
├── uploads/                  # Temporary file storage (volume mounted)
├── .env                      # Local configuration (port, feature flags)
├── Dockerfile
├── docker-compose.yml
└── docs/                     # This file and related docs
```

## Adding a file handler

1. Create a new `.py` file in `handlers/`, named `<type>_handler.py`.
2. Define `SUPPORTED_EXTENSIONS = {"ext1", "ext2"}` (lowercase) and a `scrub(file_path)` function.
3. That's it — `handlers/__init__.py` auto-discovers any `*_handler.py` module and registers it by extension at startup.

## Adding a postprocessor

1. Create a `.py` file in `postprocessors/`.
2. Implement a callable, e.g. `generate_hash(...)`.
3. Gate it behind a `.env` flag if it should be optional (e.g. `ALLOW_HASH=true`).
4. Wire the conditional call into `routes/upload.py`.

## Rebuilding the container

Changed Python code or added files: `docker-compose up --build`.

Changed only `.html`, `.css`, or `.js`: just refresh the browser, no rebuild needed.

## Testing

There's no formal test suite yet. To sanity-check changes:

- Run locally with `docker-compose up --build`.
- Drop files from `dev/generated_dirty_files_for_test/` into the web UI and confirm the output is actually clean.
- Watch the console for errors or stack traces.

## Ideas for later

- Headless mode (for use over SSH or in a TUI)
- EXIF-only fast-scrub mode
- PGP decryption support
- Drag-and-drop for multiple files in one pass

## License

MIT.
