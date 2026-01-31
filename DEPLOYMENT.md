# CompliCopilot Deployment Guide 🚀

## Current Deployment

| Component | URL | Status |
|-----------|-----|--------|
| Frontend | https://hackforge-2005.web.app | ✅ Live |
| Backend | https://complicopilot-backend.onrender.com | ⏳ Needs Deploy |

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────────────┐     ┌───────────────────────────┐   │
│   │   Firebase Hosting   │────▶│    Render Backend         │   │
│   │   (Static Frontend)  │ API │    (FastAPI + OCR)        │   │
│   │                      │     │                           │   │
│   │ hackforge-2005.web.app│     │ complicopilot-backend.    │   │
│   │                      │     │ onrender.com              │   │
│   └──────────────────────┘     └───────────────────────────┘   │
│                                            │                    │
│                                            ▼                    │
│                                ┌───────────────────────┐        │
│                                │    PostgreSQL DB      │        │
│                                │    (Render Free)      │        │
│                                └───────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Deploy Backend to Render (Free Tier)

### Option A: Deploy via Dashboard

1. Go to [render.com](https://render.com) and sign in
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `complicopilot-backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Branch**: `main`
   - **Region**: Oregon (US West)
   - **Instance Type**: Free
5. Add Environment Variables:
   ```
   DATABASE_URL=sqlite:///./complicopilot.db
   TESSERACT_CMD=/usr/bin/tesseract
   CORS_ORIGINS=https://hackforge-2005.web.app,https://hackforge-2005.firebaseapp.com
   PYTHONUNBUFFERED=1
   ```
6. Click **Deploy Web Service**

### Option B: Deploy via Blueprint (render.yaml)

1. Go to [render.com/blueprints](https://render.com/blueprints)
2. Click **New Blueprint Instance**
3. Select this repository
4. Render will auto-detect `render.yaml`
5. Review and deploy

---

## Step 2: Update Frontend API URL

After backend is deployed, update the API URL:

1. Edit `frontend/public/assets/js/api-config.js`
2. Replace the production URL with your actual Render URL:
   ```javascript
   // Around line 13
   return 'https://YOUR-ACTUAL-RENDER-URL.onrender.com';
   ```
3. Redeploy frontend:
   ```bash
   firebase deploy --only hosting
   ```

---

## Step 3: (Optional) Add PostgreSQL Database

For persistent data instead of SQLite:

1. In Render dashboard, create **New +** → **PostgreSQL**
2. Choose Free tier
3. Copy the **Internal Database URL**
4. Update your Web Service environment:
   ```
   DATABASE_URL=postgres://user:pass@host/db
   ```

---

## Local Development

### Run with Docker Compose (Recommended)

```bash
cd docker
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: PostgreSQL on port 5432

### Run Separately

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

**Frontend:**
```bash
cd frontend
npx http-server public -p 3000
```

---

## Environment Variables

### Backend (Production)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL or SQLite URL | `sqlite:///./app.db` |
| `TESSERACT_CMD` | Path to tesseract binary | `/usr/bin/tesseract` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `https://example.com` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Frontend

The frontend automatically detects the environment via `api-config.js`:
- **Production**: Uses configured backend URL
- **Local (port 3000)**: Uses `http://localhost:8000`
- **Local (port 5500)**: Uses `http://localhost:8080`

---

## Troubleshooting

### CORS Errors
- Ensure `CORS_ORIGINS` includes your frontend URL (with https://)
- No trailing slashes in origins

### 502 Bad Gateway on Render
- Check Render logs for startup errors
- Ensure Dockerfile builds successfully
- Verify health check endpoint `/api/health` returns 200

### Firebase Deploy Fails
- Run `firebase login` to re-authenticate
- Check `firebase.json` configuration
- Verify `frontend/public` directory exists

---

## Useful Commands

```bash
# Firebase
firebase login                    # Authenticate
firebase deploy --only hosting    # Deploy frontend
firebase serve                    # Local preview

# Render CLI (optional)
render login
render deploy

# Docker
docker-compose up --build         # Build and start
docker-compose down               # Stop all
docker logs docker-backend-1      # View backend logs
```

---

## CI/CD (Optional)

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install -g firebase-tools
      - run: firebase deploy --only hosting --token \${{ secrets.FIREBASE_TOKEN }}
```

Get Firebase token: `firebase login:ci`

---

## Support

- **Firebase Docs**: https://firebase.google.com/docs/hosting
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
