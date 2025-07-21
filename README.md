MetaScrub

MetaScrub is a local-first, extensible metadata scrubber designed to prioritize privacy. It runs entirely on your machine — no cloud, no telemetry, no tracking.

📁 Upload files through a simple drag-and-drop interface and get cleaned versions with sensitive metadata removed. Optionally apply hashing or GPG encryption before download.
🔍 Purpose

MetaScrub is built for:

    Journalists and whistleblowers

    Privacy advocates

    Security professionals

    Anyone who wants total control over file sanitation

The architecture is modular, allowing easy extension through file-type-specific "handlers" and optional "postprocessors."
✅ Supported File Types

Built-in handlers currently support:

    JPEG — strips EXIF metadata via Pillow

    PDF — removes embedded metadata using PyMuPDF

    DOCX — clears author/history via python-docx

    XLSX — strips metadata using openpyxl

More formats can be added by dropping new handler modules into handlers/.
🔐 Postprocessors (Optional)

Postprocessors are applied after metadata has been stripped. Currently supported:

    ✅ SHA256 hash generation — generates a .sha256.txt for verification

    ✅ GPG encryption — encrypts cleaned files using a provided public key

Toggle these options via checkboxes in the UI.
✨ Features

    🧼 Local-first metadata scrubbing

    📂 Drag & drop browser interface

    🔌 Extensible: add handlers/postprocessors easily

    🔒 Optional GPG encryption and SHA256 hashing

    🧹 Temporary-only storage — nothing persisted

    🎨 Light/dark/system theme toggle

    🐳 Fully Dockerized for clean deployment

    🔧 Configurable port and settings via .env

🚀 Quickstart

Build and run with Docker:

docker build -t metascrub .
docker run -p 8574:8574 metascrub

Or with Docker Compose:

docker-compose up --build

Then open your browser to:
http://localhost:8574
📁 Project Structure

MetaScrub/
├── app.py                # Main Flask application
├── handlers/             # File-type-specific scrubbers (JPEG, PDF, DOCX, XLSX)
├── postprocessors/       # Optional processors like hashing and encryption
├── static/               # Styles, scripts, icons
├── templates/            # Jinja2 HTML templates
├── Dockerfile            # Build configuration
├── docker-compose.yml    # Local dev orchestration
├── .env                  # Environment config (e.g., port)
├── requirements.txt      # Python dependencies
└── README.md             # You're looking at it

🛡️ Privacy Principles

    ❌ No file ever leaves your machine

    ❌ No third-party analytics

    ✅ Temporary files are wiped immediately after download

    ✅ Encryption is optional and fully under user control

🛠️ Roadmap

Add support for PNG, video, and audio files

More robust GPG key validation

One-click secure wiping

Batch download support

    Configurable scrubbing presets

📦 Dependencies

Included automatically in Docker builds:

    Python 3.9+

    Flask

    Pillow

    PyMuPDF (fitz)

    python-docx

    openpyxl

    Optional: gpg installed on host for encryption support

📝 License

Licensed under the MIT License.
🤝 Contributions

PRs and issues welcome.

If you have ideas for new handlers, postprocessors, or features, feel free to open an issue or submit a PR.
💬 Contact

Maintained by KitQuietDev
GitHub: https://github.com/KitQuietDev