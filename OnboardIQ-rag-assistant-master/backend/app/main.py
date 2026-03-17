"""
OnboardIQ API — Production Entry Point
Initializes the RAG pipeline and mounts API routers.
Falls back to demo mode if OPENAI_API_KEY is not configured.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("onboardiq")

# --- Globals for pipeline components ---
ingestion_pipeline = None
retriever = None
generator = None
DEMO_MODE = False


def _init_rag_pipeline():
    """Attempt to initialise the full RAG pipeline.
    Returns True on success, False on failure (falls back to demo mode).
    """
    global ingestion_pipeline, retriever, generator, DEMO_MODE

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — running in DEMO mode")
        DEMO_MODE = True
        return False

    try:
        from app.core.ingestion import IngestionPipeline
        from app.core.retrieval import HybridRetriever
        from app.core.generation import AnswerGenerator

        logger.info("Initializing RAG pipeline …")
        ingestion_pipeline = IngestionPipeline()
        retriever = HybridRetriever(ingestion_pipeline)
        generator = AnswerGenerator()
        logger.info("RAG pipeline ready")

        # Inject dependencies into routers
        from app.api import chat as chat_module
        from app.api import documents as docs_module

        chat_module.set_dependencies(retriever, generator)
        docs_module.set_dependencies(ingestion_pipeline, retriever, generator)

        DEMO_MODE = False
        return True

    except Exception:
        logger.exception("Failed to initialize RAG pipeline — falling back to DEMO mode")
        DEMO_MODE = True
        return False


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle."""
    _init_rag_pipeline()
    yield
    logger.info("Shutting down OnboardIQ")


# --- App creation ---
app = FastAPI(
    title="OnboardIQ API",
    version="1.0.0",
    description="AI-powered RAG system for employee onboarding",
    lifespan=lifespan,
)

# --- CORS ---
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate limiting ---
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled")
except ImportError:
    limiter = None
    logger.warning("slowapi not installed — rate limiting disabled")


# --- Global exception handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."},
    )


# ===================== Core routes =====================

@app.get("/")
def root():
    return {
        "message": "OnboardIQ API",
        "status": "online",
        "mode": "demo" if DEMO_MODE else "production",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Detailed health check — verifies each subsystem."""
    checks = {
        "api": True,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "database_connected": False,
        "mode": "demo" if DEMO_MODE else "production",
    }

    # Check ChromaDB
    if ingestion_pipeline is not None:
        try:
            count = ingestion_pipeline.collection.count()
            checks["database_connected"] = True
            checks["total_chunks"] = count
        except Exception:
            logger.warning("ChromaDB health check failed")

    overall = "healthy" if checks["api"] else "degraded"
    return {"status": overall, **checks}


@app.get("/stats")
def get_stats():
    if DEMO_MODE or ingestion_pipeline is None:
        return {
            "total_documents": 0,
            "total_chunks": 0,
            "unique_files": 0,
            "documents": [],
            "embedding_model": "text-embedding-3-small",
            "llm_model": "gpt-4o-mini",
            "mode": "demo",
        }

    stats = ingestion_pipeline.get_stats()
    return {
        "total_documents": stats["unique_documents"],
        "total_chunks": stats["total_chunks"],
        "unique_files": stats["unique_documents"],
        "documents": stats["documents"],
        "embedding_model": "text-embedding-3-small",
        "llm_model": "gpt-4o-mini",
        "mode": "production",
    }


# ===================== Mount API routers =====================
# Routers are always mounted. If the pipeline isn't initialized,
# the endpoints return helpful error messages via their dependency checks.
try:
    from app.api.chat import router as chat_router
    from app.api.documents import router as documents_router

    app.include_router(chat_router)
    app.include_router(documents_router)
    logger.info("API routers mounted")
except ImportError:
    logger.warning("Could not import API routers — only root endpoints available")

    # Minimal fallback endpoints when routers can't be imported
    from pydantic import BaseModel
    from typing import List

    class _DemoChatRequest(BaseModel):
        query: str
        conversation_history: list = []
        top_k: int = 5

    @app.post("/chat/query")
    def demo_chat(request: _DemoChatRequest):
        return {
            "answer": f"[DEMO] Pipeline not available. Query: '{request.query}'",
            "citations": [],
            "confidence": 0.0,
            "sources_used": 0,
            "retrieved_chunks": 0,
            "query": request.query,
        }

    @app.get("/documents/list")
    def demo_list():
        return {"total_documents": 0, "total_chunks": 0, "documents": []}

    @app.post("/chat/feedback")
    def demo_feedback(data: dict):
        return {"success": True, "message": "Feedback received"}

