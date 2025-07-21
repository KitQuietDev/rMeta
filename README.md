# MetaScrub

**MetaScrub** is a local-first metadata scrubber for images, PDFs, and DOCX files.

📁 **Drag & drop** your files in the browser, and receive cleaned versions with privacy-sensitive metadata removed — no cloud, no tracking.

---

## ✨ Features

- 🖼️ Removes EXIF metadata from JPEG images
- 📄 Clears PDF document metadata
- 📝 Creates clean DOCX files without embedded author or edit history
- 🔐 Optional SHA256 hash generation and GPG encryption
- 🖥️ Simple browser-based UI
- 🐳 Dockerized for easy setup
- 🧹 Temporary files only — nothing is stored after download
- ⚙️ Runs locally on port `8574` (configurable via `.env`)

---

## 🚀 Quickstart

Build and run via Docker:

```bash
docker build -t metascrub .
docker run -p 8574:8574 metascrub
```

Then open your browser to:

```
http://localhost:8574
```

Or, with Docker Compose:

```bash
docker-compose up --build
```

---

## 📁 Project Structure

```
MetaScrub/
├── app.py                # Main Flask app
├── handlers/             # File-type-specific cleaners
├── postprocessors/       # Optional hashing and GPG encryption
├── static/               # CSS, JS, favicon, etc.
├── templates/            # HTML templates (Jinja2)
├── Dockerfile            # Base image and build steps
├── docker-compose.yml    # Local orchestration
├── .env                  # Environment config (port, etc.)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🛡️ Privacy Notes

MetaScrub is designed for **maximum local privacy**:

- ✅ No file ever leaves your machine  
- ✅ No third-party analytics, logging, or telemetry  
- ✅ Temporary files are deleted after each download  

You control everything — even encryption can be added on your terms.

---

## 🔧 Configuration

You can modify `.env` to set the listening port and other options.

---

## 📦 Dependencies

- Python 3.9+
- Flask
- Pillow (for JPEGs)
- PyMuPDF / fitz (for PDFs)
- python-docx (for DOCX files)
- Optional: `gpg` installed on host if using encryption

These are bundled automatically when using Docker.

---

## 🛠️ Roadmap

- [ ] Add support for PNG and video metadata  
- [ ] UI enhancements for larger batch uploads  
- [ ] Theme-aware UI toggle (in progress)  
- [ ] One-click secure file wiping after processing  

---

## 📝 License

_Add a license here (MIT, GPL-3.0, or Apache-2.0 recommended)_

---

## 🤝 Contributions

Pull requests and issues are welcome.

If you have ideas for improving local-first privacy tools, feel free to reach out or fork the project!

---

**Built with care by [KitQuietDev](https://github.com/KitQuietDev)** 🛡️
