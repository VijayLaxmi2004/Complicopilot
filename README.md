CompliCopilot — PWA Prototype
================================

CompliCopilot is a Progressive Web App (PWA) that helps small businesses capture receipts and automatically extract, validate, and categorize expense data using OCR and AI.

This repo contains a static frontend prototype (HTML/CSS/JS), backend scaffolding, and Docker configuration to evolve into a full prototype.

Monorepo layout
- frontend/: static PWA pages, assets, and a simple dev server
- backend/: API scaffold (to be implemented with FastAPI)
- cloud/: stubs for OCR/AI modules
- docker/: Dockerfiles and docker-compose.yml for local stack
- docs/: design and architecture docs

Quick start (frontend only)
1) Install Node.js 18+
2) Start a static server from `frontend/`:
	 - Windows PowerShell:
		 npm init -y; npm install http-server --save-dev; npm run start
	 - Or run from workspace root (Docker section below for containers)

By default, the dev server serves at http://localhost:3000/frontend/pages/index.html

Frontend pages
- index.html (landing)
- auth.html (sign in/up)
- dashboard.html (mock dashboard)
- upload.html (drag-and-drop upload + simulated processing + review)

Phase 0 readiness
- Fixed CSS var `--text-muted` and added loading spinner + toasts.
- Pages load assets via `../public/...` paths.

Docker (local, optional)
Note: The current compose file expects a FastAPI backend and Postgres. Until the backend is implemented, only the frontend service is useful.

From the repo root:
	- docker-compose -f docker/docker-compose.yml up --build

Known gaps (to be addressed in Phase 1+)
- Service worker + manifest for PWA install/offline
- FastAPI API endpoints and DB migrations
- OCR/AI integrations and background processing

Troubleshooting
- If assets 404, ensure you open pages under `/frontend/pages/...` when using a static server.
- If using Docker for the frontend, confirm the Docker build context and COPY paths match the `frontend/` layout.

License
MIT (pending)
