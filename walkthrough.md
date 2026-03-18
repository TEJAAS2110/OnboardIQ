# Production Readiness — Walkthrough

## Summary

Implemented **12 production-readiness improvements** across backend and frontend for OnboardIQ, making it deployment-ready on **Render (backend)** + **Vercel (frontend)**.

---

## Backend Changes

### Core Architecture
- **[main.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/main.py)** — Fully rewritten to mount real RAG pipeline routers with a graceful demo-mode fallback when `OPENAI_API_KEY` is not set

### Structured Logging
Replaced all `print()` emoji statements with Python `logging` module across **7 files**:
- [core/ingestion.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/core/ingestion.py), [core/retrieval.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/core/retrieval.py), [core/generation.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/core/generation.py)
- [api/chat.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/api/chat.py), [api/documents.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/api/documents.py)
- [utils/document_processor.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/utils/document_processor.py), [utils/chunking.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/utils/chunking.py)

### Security & Reliability

| Improvement | File |
|------------|------|
| CORS hardening (env-based origins) | [main.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/main.py) |
| Rate limiting via `slowapi` | [main.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/main.py) |
| Global exception handler | [main.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/main.py) |
| OpenAI retry (3× exponential backoff) | [core/generation.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/core/generation.py) |
| Filename sanitization (path traversal prevention) | [api/documents.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/api/documents.py) |
| Real health checks (ChromaDB, OpenAI key) | [main.py](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/app/main.py) |

### New Files

| File | Purpose |
|------|---------|
| [requirements.txt](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/requirements.txt) | Added 4 missing deps + slowapi |
| [.env.example](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/.env.example) | Documented env template |
| [Procfile](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/backend/Procfile) | Render start command |
| [render.yaml](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/render.yaml) | One-click Render deployment |
| [.gitignore](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/.gitignore) | Root gitignore for both stacks |

---

## Frontend Changes

| Change | File |
|--------|------|
| Env-based API URL (`VITE_API_URL`) | [api.js](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/src/services/api.js) |
| Request timeouts (60s queries, 120s uploads) | [api.js](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/src/services/api.js) |
| Toast notifications replacing all `alert()` | [App.jsx](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/src/App.jsx), [ChatInterface.jsx](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/src/components/Chat/ChatInterface.jsx) |
| Toast CSS (slide-in animation) | [App.css](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/src/App.css) |
| Centralized API URL (no more hardcoded localhost) | [App.jsx](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/src/App.jsx) |

### New Files

| File | Purpose |
|------|---------|
| [.env.development](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/.env.development) | Local dev → `http://localhost:8000` |
| [.env.production](file:///c:/Users/tejas%20panu/Downloads/OnboardIQ-rag-assistant-master/OnboardIQ-rag-assistant-master/frontend/.env.production) | Production → Render URL |

---

## Verification

✅ **Frontend build** — `npm run build` succeeded (69 modules, 75KB gzipped)

---

## Deployment Steps

### Backend → Render

1. Push code to **GitHub**
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set **Root Directory** to `backend`
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. Add **Environment Variable**: `OPENAI_API_KEY` = your key
8. Add **Environment Variable**: `ALLOWED_ORIGINS` = your Vercel URL
9. Deploy!

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project**
2. Import your GitHub repo
3. Set **Root Directory** to `frontend`
4. Set **Environment Variable**: `VITE_API_URL` = your Render backend URL
5. Deploy!
6. Copy the Vercel URL and add it to Render's `ALLOWED_ORIGINS`
