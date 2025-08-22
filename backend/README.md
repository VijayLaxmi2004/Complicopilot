Backend (FastAPI) — CompliCopilot
=================================

Status: scaffolded
- FastAPI app with a root health endpoint.
- Ready to extend with receipts, insights, and compliance routes.

Run locally (dev)
- Create a virtual environment (optional but recommended)
  - py -3 -m venv .venv
  - .venv\Scripts\activate
- Install deps
  - pip install -r requirements.txt
- Start server
  - uvicorn main:app --reload --port 8000

Endpoints (current)
- GET / → { status: "ok", service: "backend", version: "0.1.0" }

Planned endpoints (MVP)
- GET /receipts?query&filters&sort&page
- GET /receipts/{id}
- GET /insights/summary?date_range
- GET /compliance/issues?status
- POST /receipts (upload)
- POST /receipts/bulk/approve
- PATCH /receipts/{id}

Project layout
- main.py — FastAPI app
- api/ — route modules (planned)
- models/ — Pydantic models (planned)
- database/ — DB setup/migrations (planned)

Notes
- Keep secrets out of the repo; use environment variables.
- Prefer pydantic v2 models; validate inputs at the edges.
