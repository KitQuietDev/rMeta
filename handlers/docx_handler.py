import docx
import os

supported_extensions = {"docx"}

def scrub(file_path):
    try:
        doc = docx.Document(file_path)
        new_doc = docx.Document()
        for para in doc.paragraphs:
            new_doc.add_paragraph(para.text)
        cleaned_path = file_path.replace(".docx", "_cleaned.docx")
        new_doc.save(cleaned_path)
        os.replace(cleaned_path, file_path)
    except Exception as e:
        print(f"Error scrubbing DOCX metadata: {e}")
