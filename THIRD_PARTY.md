# Third-party libraries

Libraries rMeta actually depends on at runtime, and the license each is distributed under. License info here is a courtesy summary, not legal advice — check each project's own license file if you need certainty.

| Library | Purpose | Used in | License |
|---|---|---|---|
| Flask | Web framework | `app.py`, `renderer/flask_renderer.py` | BSD-3-Clause |
| Werkzeug | WSGI utilities (Flask dependency) | Flask internals | BSD-3-Clause |
| Jinja2 | Templating | `templates/` | BSD-3-Clause |
| gunicorn | Production WSGI server | production deployments | MIT |
| python-dotenv | `.env` loading | `config.py` | BSD-3-Clause |
| click | CLI argument parsing (Flask dependency) | Flask internals | BSD-3-Clause |
| PyYAML | YAML parsing | config/tooling | MIT |
| typing_extensions | Typing backports | type hints | PSF-2.0 |

The following are dependencies of [rmeta-core](https://github.com/KitQuietDev/rmeta-core) (the shared handler/postprocessor package this repo pulls in via `requirements.txt`), rather than direct dependencies of this repo:

| Library | Purpose | License |
|---|---|---|
| pypdf | PDF metadata handling | BSD-3-Clause |
| pdfplumber / pdfminer.six | PDF text extraction (for PII scanning) | MIT |
| python-docx | Word document parsing | MIT |
| openpyxl | Excel file parsing | MIT |
| pillow | Image handling | MIT-CMU |
| pillow_heif | HEIC/HEIF decoding | BSD-3-Clause |
| piexif | EXIF read/write | MIT |
| pyheif | HEIC decoding | LGPL-3.0 |
| nometa | Metadata stripping helper | MIT |
| lxml | XML processing | BSD-3-Clause |
| cryptography | Crypto primitives | Apache-2.0 / BSD-3-Clause (dual) |
| psutil | Memory/resource checks | BSD-3-Clause |
| aiofiles | Async file I/O | Apache-2.0 |

GPG encryption (in `rmeta-core`'s `postprocessors/gpg_encryptor.py`) shells out to the system's own `gpg` binary rather than bundling a GPG library — that binary's license is whatever your OS/distribution provides.

## Development tooling

Not shipped in the running app — used for linting, formatting, and pre-commit hooks during development: `black`, `pre-commit`, `pyflakes`, `pycodestyle`, `mccabe`, `mypy_extensions`, `virtualenv`, `filelock`, `platformdirs`, `identify`, `cfgv`, `nodeenv`, `distlib`.

Thanks to the maintainers of all of the above.
