# rMeta

rMeta strips metadata from files before you share them. It runs entirely on your own machine (or your own container) and never sends anything over the network.

Drop a file in, rMeta scrubs it, you get a clean copy out.

## What it does

- Removes metadata from JPEG, PDF, DOCX, XLSX, HEIC, TXT, and CSV files
- Runs locally, inside Docker — no external calls, no telemetry
- Optional SHA256 hash generation for the cleaned output
- Optional GPG encryption of the output using your own public key
- Auto-cleans its temporary workspace on startup, shutdown, new uploads, and on demand from the UI

## Supported file types

| Type | What happens |
|------|--------------|
| JPEG | EXIF and other metadata stripped in place |
| PDF  | Metadata fields cleaned via `pypdf` |
| DOCX | Metadata stripped from the underlying XML |
| XLSX | Metadata tags removed |
| HEIC | Converted to JPEG, then scrubbed |
| TXT / CSV | Checked for embedded metadata (rare, but handled) |

Nothing here is a forensic guarantee — see the Privacy Notes below for the honest version.

## Getting started

Pick whichever fits how you work. All three run rMeta locally.

**Quickest — just run the published image:**

```bash
docker run --rm -d -p 8574:8574 ghcr.io/kitquietdev/rmeta:latest
```

No volumes, no persistence, no config. Good for a quick test.

**Docker Compose — if you want config and persistence:**

```bash
mkdir rmeta && cd rmeta
curl -O https://raw.githubusercontent.com/KitQuietDev/rMeta/main/docker-compose.yml
docker compose up -d
```

Runs under Gunicorn with production settings.

**From source — for development or customization:**

```bash
git clone https://github.com/KitQuietDev/rMeta.git
cd rMeta
cp docker-compose.yml.example docker-compose.yml
docker compose up
```

Runs in development mode with hot reload and mounted volumes. Edit the copied `docker-compose.yml` as needed for your setup.

**Do not expose the development setup to the internet.** See the security warning below.

---

Want a pure command-line workflow instead? Check out [rMetaCLI](https://github.com/KitQuietDev/rMetaCLI), the CLI counterpart to this project.

## Security warning

rMeta's development mode (`flask run`) is not hardened and should not be exposed publicly:

- No production-grade request handling
- No header sanitization or enforced TLS
- Intended for local testing only

If you expose rMeta publicly — reverse proxy, tunnel, port forwarding — that's on you to secure. There's no built-in proxy-awareness or TLS support yet.

## Architecture

- `app.py` / `wsgi.py` — entry points
- `renderer/flask_renderer.py` — Flask app setup
- `routes/` — upload, download, and session-cleanup endpoints
- `uploads/` — temporary workspace, wiped automatically

File handlers, postprocessors, and cleanup/chunking/PII-scanning utilities live in [rmeta-core](https://github.com/KitQuietDev/rmeta-core), shared with [rMetaCLI](https://github.com/KitQuietDev/rMetaCLI). This repo pulls it in via `requirements.txt`.

## Privacy notes

rMeta does best-effort cleaning with MIT-compatible libraries. It's not a substitute for verification with dedicated tools if you need certainty:

- **JPEG:** standard EXIF removed; adversarial/corrupt files may retain data
- **PDF:** most metadata fields cleaned; hidden or embedded content may persist
- **DOCX:** XML metadata stripped; revision history or embedded objects may remain
- **XLSX:** metadata tags removed; hidden sheets or comments are possible
- **HEIC:** converted and scrubbed; proprietary tags may linger
- **TXT/CSV:** no embedded metadata, but filesystem attributes (timestamps, permissions) are untouched

## Development artifacts

`dev/` holds sample "dirty" files and a small script used to sanity-check handlers during development. It's not a test suite — just fixtures for manually exercising each handler.

## License

MIT — see [`LICENSE`](LICENSE). Third-party dependencies and their licenses are listed in [`THIRD_PARTY.md`](THIRD_PARTY.md).

## Contributing

New file-type handler, UI tweak, bug fix — contributions are welcome. See:

- [Code of Conduct](docs/CODE_OF_CONDUCT.md)
- [Contributing guide](docs/CONTRIBUTING.md)
- [Developer notes](docs/DEVELOPERS.md)

For version history, see [`changelog.md`](changelog.md).
