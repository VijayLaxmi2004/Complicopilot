📋 CompliCopilot — PWA Prototype ✨
====================================

🚀 CompliCopilot is a Progressive Web App (PWA) that helps small businesses capture receipts and automatically extract, validate, and categorize expense data using OCR and AI.

📦 This repo contains a static frontend prototype (HTML/CSS/JS), backend scaffolding, and Docker configuration to evolve into a full prototype.

## 🏏 Team: Strikers

👥 **Team Members:**
- Member 1: [ID Portal](https://portal.example.com/member1)
- Member 2: [ID Portal](https://portal.example.com/member2)  
- Member 3: [ID Portal](https://portal.example.com/member3)
- Member 4: [ID Portal](https://portal.example.com/member4)

*Note: Please update with actual team member names and ID portal links*

## 📁 Monorepo layout
- 🎨 **frontend/**: static PWA pages, assets, and a simple dev server
- ⚡ **backend/**: API scaffold (to be implemented with FastAPI)
- ☁️ **cloud/**: stubs for OCR/AI modules
- 🐳 **docker/**: Dockerfiles and docker-compose.yml for local stack
- 📚 **docs/**: design and architecture docs

## 🚀 Quick start (frontend only)
1) 📥 Install Node.js 18+
2) 🌐 From `frontend/`, serve static files (use any static server). Example with http-server:

	**PowerShell:**
	- `npm init -y`
	- `npm install http-server --save-dev`
	- `npx http-server -p 3000 ..\ -c-1`

🌍 By default, open: http://localhost:3000/frontend/pages/index.html

## 📱 Frontend pages
- 🏠 **index.html** (landing)
- 🔐 **auth.html** (sign in/up)
- 📊 **dashboard.html** (mock dashboard)
- 📤 **upload.html** (drag-and-drop upload + simulated processing + review)

## ✅ Implemented so far
- ✨ Ambient glow on auth with cursor-tracing spotlight; loading overlay spinner
- 👨‍💻 Dev-only “Sign in as Dev Admin” shortcut (localStorage stub) on auth page.
- 🎯 Home and dashboard icons added; button alignment and header polish.
- 📋 Upload flow with drag-and-drop and simulated processing + review.

## 🐳 Docker (optional)
🎯 The compose targets a FastAPI backend and Postgres. Frontend can be served statically without Docker.

📂 From repo root:
- `docker-compose -f docker/docker-compose.yml up --build`

## 🔮 Next steps (Phase 1+)
- 📱 Service worker + manifest (PWA install/offline)
- ⚡ FastAPI endpoints for receipts, insights, compliance
- 🤖 Background OCR/AI integration and queue
- 📊 Dashboard filters, details drawer, charts; bulk actions

## 🔧 Troubleshooting
- ❗ If assets 404, ensure you open pages under `/frontend/pages/...` when using a static server
- 🐳 If using Docker for the frontend, confirm the Docker build context and COPY paths match the `frontend/` layout

## 👨‍💻 Dev admin sign-in
- 🔑 On auth page, click “Sign in as Dev Admin” to jump to the dashboard (stores a mock user in localStorage).

## 🌿 Git workflow (suggested)
- 🌱 Create a feature branch: `git checkout -b feat/ui-auth-glow`
- 💾 Commit and push: `git add . && git commit -m "feat: ui updates" && git push -u origin feat/ui-auth-glow`
- 🔄 Open a PR to main

## 📄 License
📜 MIT (pending)
