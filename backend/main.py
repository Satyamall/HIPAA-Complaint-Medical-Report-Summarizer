from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from transformers import pipeline
from PyPDF2 import PdfReader
import os, uuid, re

app = FastAPI()

UPLOAD_DIR = "uploads"
SUMMARY_DIR = "summaries"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SUMMARY_DIR, exist_ok=True)

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Extract text from PDF
def extract_text(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        raise RuntimeError(f"Failed to read PDF: {e}")

# Deidentify PII text
def deidentify(text: str) -> str:
    return re.sub(r"(Name|DOB|Patient ID|Date of Birth)[^\n]*", "[REDACTED]", text, flags=re.I)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), consent: bool = Form(...)):
    if not consent:
        raise HTTPException(status_code=400, detail="HIPAA consent not provided.")

    # Generate a unique file ID
    file_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # Save uploaded file
    try:
        with open(pdf_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Process the PDF
    try:
        text = extract_text(pdf_path)
        clean_text = deidentify(text)

        # Truncate to max model input length (~1024 tokens ≈ 4000 characters)
        input_text = clean_text[:4000]

        summary = summarizer(input_text, max_length=150, min_length=40, do_sample=False)[0]["summary_text"]

        # Save the summary
        summary_path = os.path.join(SUMMARY_DIR, f"{file_id}.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during summarization: {e}")

    # Return the summary
    return get_summary(file_id)

# Helper to retrieve saved summary
def get_summary(summary_id: str):
    path = os.path.join(SUMMARY_DIR, f"{summary_id}.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return {"summary_id": summary_id, "summary": f.read()}
    raise HTTPException(status_code=404, detail="Summary not found.")
