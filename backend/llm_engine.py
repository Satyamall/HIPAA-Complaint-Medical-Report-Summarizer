
# llm_engine.py

from transformers import pipeline

# Load once at startup
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(report_text: str) -> str:
    # Limit input length to fit model constraints (~1024 tokens ≈ 4000 characters)
    input_text = report_text[:4000]

    try:
        summary = summarizer(input_text, max_length=150, min_length=40, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        return f"Summary generation failed: {e}"

# def generate_summary(report_text: str) -> str:
#     prompt = f"Summarize this CBC report for a patient: {report_text}"
#     return "This is a placeholder summary. The report indicates normal hemoglobin and WBC levels."

