👩‍💻 DEVELOPERS.md

Welcome to MetaScrub — a fast, clean, containerized tool for scrubbing metadata from sensitive files. If you're here, you're either curious, contributing, or critiquing — and you are absolutely welcome.

This document is for developers, tinkerers, privacy nuts, field users, and anyone else who wants to extend or improve the project.

# 🧠 Project Philosophy

MetaScrub is built around a few core principles:

- Minimalism: Simple UI, focused functionality, no bloat.

- Modularity: Every handler and postprocessor is self-contained and easily swappable.

- Security-first: No metadata. Optional encryption. Designed for zero-trust environments.

- Accessibility: Clear docs, helpful comments, and low barrier to entry.

We want contributions from all experience levels — not just seasoned devs.
# 🗂️ Project Layout

.
├── app.py                     # Main Flask app
├── handlers/                 # File-type-specific metadata scrubbers
├── postprocessors/          # Optional extras (GPG, hashing)
├── static/                  # CSS and JavaScript
├── templates/               # HTML (currently only index.html)
├── uploads/                 # Temporary file storage (volume mounted)
├── .env                     # Configuration (port, feature flags)
├── Dockerfile               # Container setup
├── docker-compose.yml       # Runtime orchestration
└── docs/                    # This file and future developer docs

# 🔌 Adding a New File Handler

1. Create a new .py file in handlers/

2. Define:

```
supported_extensions = {"ext1", "ext2"}  # lowercase only
def scrub(file_path):
```

The app auto-discovers handlers at runtime.

# 🧬 Adding a Postprocessor (e.g. Hashing, Encryption)

1. Create a .py file in postprocessors/

2. Implement a callable (e.g. def generate_hash(...))

3. Use .env to toggle options (ALLOW_HASH=true, etc.)

4. app.py handles conditional execution

# 🛠️ Rebuilding the Container

If you make changes to Python code or add new files:
```
docker-compose up --build
```
If you only change .html, .css, or .js files:

✅ Just refresh the browser — no rebuild needed.
# 🤝 Contributions

Pull requests, forks, and ideas are welcome.

- Add a handler? ✅

- Suggest a privacy feature? ✅

- Tweak the UI or accessibility? ✅

- Improve docs? Yes please.

# 🧪 Testing

There’s no formal test suite yet, but:

- Run locally with docker-compose up --build

- Drop files into the web UI and confirm output

- Watch console logs for errors or stack traces

# 💡 Future Ideas

- CLI mode (for field/offline usage)

- Headless mode (for use over SSH or TUI)

- EXIF-only fast scrubber mode

- PGP decryption support (optional, advanced)

- Drag-and-drop multiple files

- Onion routing / airgapped workflows

# 🧾 License

This project is MIT licensed.

Thanks for being here. You don’t need permission to start building — you have it.