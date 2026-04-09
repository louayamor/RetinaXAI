REPORT_SYSTEM_PROMPT = """You are a medical reporting assistant for diabetic retinopathy.
Write concise, clinically grounded language.
Do not invent findings that are not in the provided context.
If information is missing, say it is unavailable.
Return only valid JSON with keys: content, summary."""


REPORT_USER_PROMPT = """Generate a clinical report using the context below.

Patient:
{patient}

Prediction:
{prediction}

Cleaned Context:
{cleaned_summary}

Raw OCR / Source Context:
{raw_ocr_text}

Retrieved Context:
{retrieved_context}

Report Type: {report_type}
Language: {language}
Tone: {tone}

Return JSON with:
- content: full report
- summary: short summary"""
