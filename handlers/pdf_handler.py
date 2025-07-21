import fitz  # PyMuPDF
import os

supported_extensions = {"pdf"}

def scrub(file_path):
    try:
        doc = fitz.open(file_path)
        doc.set_metadata({key: "" for key in doc.metadata})
        cleaned_path = file_path + "_cleaned.pdf"
        doc.save(cleaned_path)
        doc.close()
        os.replace(cleaned_path, file_path)
    except Exception as e:
        print(f"Error scrubbing PDF metadata: {e}")
