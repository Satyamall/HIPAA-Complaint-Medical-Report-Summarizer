from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from llm_engine import generate_summary
from pdf_parser import extract_text
import os
import tempfile
from pathlib import Path

app = FastAPI()

# Allow frontend to connect (e.g., from localhost:3000)
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...), consent: bool = Form(...)):
    if not consent:
        return {"error": "User consent not given."}

    # Read the file content
    contents = await file.read()

    # Save file to a temp directory
    temp_dir = tempfile.gettempdir()
    filepath = Path(temp_dir) / file.filename

    try:
        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception as e:
        return {"error": f"Failed to save uploaded file: {e}"}

    try:
        # Extract and summarize
        report_text = extract_text(str(filepath))
        summary = generate_summary(report_text)

        # Replace sensitive placeholder
        summary = summary.replace("Satya Prakash Mall", "[PATIENT]")

        return {"summary": summary}

    except Exception as e:
        return {"error": f"Processing failed: {e}"}
