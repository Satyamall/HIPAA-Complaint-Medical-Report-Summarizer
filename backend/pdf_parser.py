# pdf_parser.py

from PyPDF2 import PdfReader

def extract_text(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text
    except Exception as e:
        return f"Failed to extract text: {e}"
