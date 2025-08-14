# 🧼 rMeta

**rMeta** is your local-first tool for cleaning metadata from sensitive files—no cloud, no tracking, no leaks. Run it entirely on your machine and take full control over digital hygiene.

📁 Just drag and drop files into the browser to get scrubbed versions back. Optionally add hashing or GPG encryption on your terms.
## 🔍 Who’s It For?

rMeta is made for:

- 🕵️ Journalists and whistleblowers  
- 🔐 Privacy advocates  
- 🛡️ Security professionals  
- 👤 Anyone who wants true digital autonomy

It’s modular, extensible, and easy to tailor via its handler-based architecture.
## ✅ What File Types Are Supported?

Out of the box:

- **JPEG** — EXIF wiped via Pillow  
- **PDF** — Metadata scrubbed via PyMuPDF  
- **DOCX** — Author/history removed via python-docx  
- **XLSX** — Cleanup via openpyxl

Want more? Just drop a custom module into `handlers/`.
## 🔐 Optional Add-ons

Post-processing extras you can toggle in the UI:

- ✅ **SHA256 Hashes** — `.sha256.txt` verification file  
- ✅ **GPG Encryption** — encrypt files using your own public key (must be uploaded)
## 🧩 Extending rMeta

Want to add support for more file types (e.g., PNG, MP4, SVG)?

1. Create a new module in `handlers/` following the examples inside.
2. Register it in `app.py` by importing it and adding to the supported types.
3. Rebuild the Docker container so the changes apply:

```bash
docker-compose build
docker-compose up
```
🛠️ You must rebuild the container (with ```docker-compose up --build```)any time you change backend Python code or add files (like handlers or postprocessors).
Changes to **.html, .js, or .css** files **do not** require a rebuild — just refresh your browser.
## ✨ Features At-A-Glance

- 🧼 Local-first processing  
- 🖥️ Browser-based UI  
- 🔌 Modular architecture (easy to extend)  
- 🔒 Optional hashing + GPG encryption  
- 🧹 Temporary files are deleted after download  
- 🎨 Light/dark/system theme toggle  
- 🐳 Dockerized for clean deploy  
- ⚙️ `.env` config for ports and tweaks
## 🚀 Get Started

Build and run with Docker:

```bash
docker build -t rMeta .
docker run -p 8574:8574 rMeta
```

Or fire it up with Docker Compose:

```bash
docker-compose up --build
```

Open your browser to:

```
http://localhost:8574
```
## 📦 Project Structure

```
rMeta/
├── app.py              # Main Flask backend
├── handlers/           # File scrubbers per format
├── postprocessors/     # Hashing, encryption
├── static/             # CSS & JS
├── templates/          # Browser interface
├── Dockerfile          # Build recipe
├── docker-compose.yml  # Container orchestration
├── .env                # Runtime config
└── requirements.txt    # Python dependencies
```
## 🛡️ Privacy-First Philosophy

- ✅ Nothing ever leaves your machine  
- ✅ No analytics, no trackers  
- ✅ Temp files wiped after download  
- ✅ Encryption is optional and fully local
## 📈 Roadmap

Coming soon:

- [ ] PNG, video, and audio support  
- [ ] Smarter GPG key validation  
- [ ] One-click file wiping  
- [ ] Batch downloads  
- [ ] Scrubbing presets (light, aggressive, etc.)
## 📋 Dependencies

Docker image bundles:

- Python 3.9+  
- Flask  
- Pillow  
- PyMuPDF (fitz)  
- python-docx  
- openpyxl  
- Optional: `gpg` installed for encryption
## 📝 License

MIT—fork it, remix it, ship it. Just give credit.
## 🤝 Contributions

PRs, issues, suggestions—all welcome.

Have an idea for a new handler or feature? Drop a line or send a pull request.
## 💬 Maintainer

Created by [KitQuietDev](https://github.com/KitQuietDev)

## 📸 Screenshots

### Upload Interface
![Upload interface](docs/images/screenshot_start.png)

### After Processing (with hash generation)
![After processing](docs/images/screenshot_result.png)
