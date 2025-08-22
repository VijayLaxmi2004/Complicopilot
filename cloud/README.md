Cloud (AI/OCR) — CompliCopilot
===============================

Status: stubs
- Placeholder for OCR (vision) and AI pipelines.

Proposed structure
- ocr/ — text extraction and image handling
- ai/ — entity extraction, categorization, compliance rules

Local dev approach
- Keep these modules callable via the backend (FastAPI) for consistency.
- Use background tasks or a simple queue for processing (Celery/RQ optional later).

MVP ideas
- Mock OCR response JSON for a few receipt samples.
- Rule-based compliance checks (GST format, required fields, confidence thresholds).

Next steps
- Define interfaces between backend and cloud modules.
- Add sample receipts and expected outputs for tests.
