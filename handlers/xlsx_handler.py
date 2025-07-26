"""
XLSX Metadata Scrubber for rMeta

Uses NoMETA to surgically remove embedded metadata from Excel .xlsx files.
Includes preflight validation for malformed XML and avoids unnecessary scrubbing.

✅ Requires: nometa (pip install nometa)
✅ Non-destructive to spreadsheet contents
✅ Optimized for audit visibility and processing speed
"""

import logging
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)
__all__ = ["scrub", "SUPPORTED_EXTENSIONS", "get_additional_messages"]

SUPPORTED_EXTENSIONS = {"xlsx"}

def scrub(file_path: str) -> None:
    path = Path(file_path)
    ext = path.suffix.lower().lstrip(".")

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    try:
        from nometa import Document, Core, App
    except ImportError:
        raise ImportError("xlsx scrubber requires NoMETA. Install with: pip install nometa")

    try:
        # Preflight validation
        doc = Document(file_path, Core, App)
        _ = doc.core.creator  # Trigger potential XML namespace error

        # Scrub metadata fields
        doc.core.creator = ""
        doc.core.lastModifiedBy = ""
        doc.core.title = ""
        doc.core.subject = ""
        doc.core.description = ""

        # Save to temp file and overwrite original
        temp_path = str(path.with_suffix(".scrubbed.xlsx"))
        doc.save(temp_path)
        shutil.move(temp_path, file_path)

        logger.info(f"📊 XLSX metadata scrubbed via NoMETA: {file_path}")
    except ValueError as e:
        if "prefix 'dc' not found" in str(e):
            logger.warning(f"⚠️ Skipping file due to malformed XML namespace: {file_path}")
            raise RuntimeError(f"{Path(file_path).name} skipped — malformed Excel metadata (missing XML prefix definitions)")
        raise
    except Exception as e:
        logger.error(f"❌ NoMETA XLSX scrub failed: {e}")
        raise RuntimeError(f"XLSX scrub error: {e}")

def get_additional_messages(file_path: str):
    messages = []
    try:
        from nometa import Document, Core, App
        doc = Document(file_path, Core, App)

        if doc.core.creator:
            messages.append(f"🕵️ Creator metadata detected: “{doc.core.creator}”")
        if doc.core.title:
            messages.append(f"🕵️ Title metadata detected: “{doc.core.title}”")
        if doc.core.subject:
            messages.append(f"🕵️ Subject metadata detected: “{doc.core.subject}”")

        return messages
    except ValueError as e:
        if "prefix 'dc' not found" in str(e):
            return [
                f"⚠️ Skipped {Path(file_path).name} — Excel metadata structure is malformed or incomplete.",
                "🛠️ Missing XML namespace definitions like 'dc:' prevent metadata inspection.",
                "📌 To fix, rebuild this file using Excel or a spreadsheet editor that generates clean XML headers."
            ]
        return [f"⚠️ Metadata inspection error in {Path(file_path).name}: {e}"]
    except Exception as e:
        return [f"⚠️ Could not inspect XLSX metadata for {Path(file_path).name}"]
