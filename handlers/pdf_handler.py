"""
PDF Metadata Scrubber for rMeta

Uses PyMuPDF (fitz) to strip all metadata from PDF files.
Saves a cleaned copy and replaces the original file.
"""

import fitz  # PyMuPDF
import os

supported_extensions = {"pdf"}


def scrub(file_path):
    """
    Scrubs metadata from a PDF file in place.

    Args:
        file_path (str): Path to the input PDF file.
    """
    try:
        doc = fitz.open(file_path)
        # Clear all metadata keys
        doc.set_metadata({key: "" for key in doc.metadata})
        cleaned_path = file_path + "_cleaned.pdf"
        doc.save(cleaned_path)
        doc.close()
        os.replace(cleaned_path, file_path)
    except Exception as e:
        print(f"Error scrubbing PDF metadata: {e}")
