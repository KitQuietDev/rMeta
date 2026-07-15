# Developer notes

Notes for anyone extending or maintaining rMeta.

## Project layout

```
.
├── app.py                    # Flask app entry point
├── renderer/flask_renderer.py # Flask app setup
├── routes/                   # Upload, download, session-cleanup endpoints
├── static/                   # CSS and JS
├── templates/                # HTML templates (currently just index.html)
├── uploads/                  # Temporary file storage (volume mounted)
├── .env                      # Local configuration (port, feature flags)
├── Dockerfile
├── docker-compose.yml
└── docs/                     # This file and related docs
```

Handlers, postprocessors, and shared utilities (cleanup, chunking, PII scanning) live in the separate [rmeta-core](https://github.com/KitQuietDev/rmeta-core) package, not in this repo — it's pulled in via `requirements.txt` and shared with rMetaCLI.

## Adding a file handler

Handlers live in `rmeta-core`, not here. In that repo:

1. Create a new `.py` file in `rmeta_core/handlers/`, named `<type>_handler.py`.
2. Define `SUPPORTED_EXTENSIONS = {"ext1", "ext2"}` (lowercase) and a `scrub(file_path)` function.
3. `rmeta_core/handlers/__init__.py` auto-discovers any `*_handler.py` module and registers it by extension at startup.
4. Tag a new `rmeta-core` release and bump the pin in this repo's `requirements.txt` to pick it up.

## Adding a postprocessor

Also in `rmeta-core`:

1. Create a `.py` file in `rmeta_core/postprocessors/`.
2. Implement a callable, e.g. `generate_hash(...)`.
3. Tag a release, bump the pin here, then gate it behind a `.env` flag if it should be optional (e.g. `ALLOW_HASH=true`) and wire the conditional call into `routes/upload.py`.

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
