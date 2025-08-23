# 🚀 CompliCopilot — Intelligent Expense Management

Welcome to **CompliCopilot**, a Progressive Web App (PWA) designed to revolutionize how small businesses manage their expenses. By leveraging **OCR** and **AI**, CompliCopilot automates receipt capture, validation, and categorization, replacing the need for junior-level accountants. 

---

## 🌟 Project Overview

### **The Idea**
CompliCopilot simplifies expense management for small businesses by automating the tedious process of receipt handling. It extracts, validates, and categorizes expense data with precision, saving time and reducing errors.

### **Problem Statement**
Small businesses often struggle with:
- Manual receipt handling.
- Errors in data entry.
- Lack of compliance with tax regulations.

### **Innovation**
- **AI-Powered Automation**: Extracts and validates data with high accuracy.
- **User-Friendly Interface**: Drag-and-drop uploads and real-time feedback.
- **Cost-Effective Solution**: Eliminates the need for junior-level accountants.

### **Market Potential**
The global market for expense management software is projected to reach **$10 billion** by 2030. CompliCopilot aims to capture a significant share by targeting small and medium-sized businesses.

---

## 🏗️ Project Architecture

### **Monorepo Layout**
- **frontend/**: Static PWA pages, assets, and a simple dev server.
- **backend/**: API scaffold built with FastAPI.
- **cloud/**: Stubs for OCR/AI modules.
- **docker/**: Dockerfiles and docker-compose.yml for local stack.
- **docs/**: Design and architecture documentation.

### **Tech Stack**
- **Frontend**: HTML, CSS, JavaScript.
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL.
- **AI/OCR**: Cloud-based AI pipelines for data extraction.
- **Deployment**: Vercel (frontend), Docker (local development).

---

## 🛠️ How We Are Building It
1. **Frontend**: A responsive PWA with drag-and-drop upload functionality.
2. **Backend**: FastAPI endpoints for receipts, insights, and compliance checks.
3. **AI Integration**: OCR for text extraction and AI for categorization.
4. **Dockerized Development**: Simplified local setup with Docker Compose.

---

## 👥 Team Strikers

We are **Team Strikers**, a group of passionate developers building innovative solutions. Meet our team:

- **Member 1**: _[Add Name]_  
  Role: _[Add Role]_  
  Expertise: _[Add Expertise]_

- **Member 2**: _[Add Name]_  
  Role: _[Add Role]_  
  Expertise: _[Add Expertise]_

- **Member 3**: _[Add Name]_  
  Role: _[Add Role]_  
  Expertise: _[Add Expertise]_

- **Member 4**: _[Add Name]_  
  Role: _[Add Role]_  
  Expertise: _[Add Expertise]_

---

## 🚀 Quick Start

### **Frontend Only**
1. Install Node.js 18+.
2. From `frontend/`, serve static files using any static server. Example:
   ```bash
   npx http-server -p 3000 ..\ -c-1
   ```
3. Open: [http://localhost:3000/frontend/pages/index.html](http://localhost:3000/frontend/pages/index.html).

### **Dockerized Setup**
1. From the repo root, run:
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```
2. Access the frontend at `http://localhost:3000` and backend at `http://localhost:8000`.

---

## 📈 Next Steps
- Add service worker and manifest for PWA install/offline support.
- Implement FastAPI endpoints for receipts, insights, and compliance.
- Integrate background OCR/AI processing.
- Enhance dashboard with filters, charts, and bulk actions.

---

## 📜 License
MIT (pending).
