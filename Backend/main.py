import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure Backend directory is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.config import settings
from app.schemas.rag import RAGRequest
from app.services.ai_service import ai_service

app = FastAPI(
    title="HR Policies RAG API",
    description="FastAPI service for HR Policies Q&A Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Phase 4: CORS Configuration
# Allow deployed Vercel frontend origin and development origins without wildcard credentials
origins = [
    "https://hr-policies-rag-chatbot-ai-powered.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Support optional custom FRONTEND_URL or ALLOWED_ORIGIN from environment
custom_frontend = os.getenv("FRONTEND_URL") or os.getenv("ALLOWED_ORIGIN")
if custom_frontend and custom_frontend not in origins:
    origins.append(custom_frontend.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ==========================================================
# 📊 Schemas
# ==========================================================
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    score_threshold: Optional[float] = 0.35
    fallback_to_llm: Optional[bool] = True


class QueryResponse(BaseModel):
    query: str
    answer: str
    status: str
    sources: Optional[List[str]] = []
    matches_count: Optional[int] = 0


# ==========================================================
# 🩺 Phase 3: Reliable Health & Status Endpoints
# ==========================================================
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health():
    """
    Standard production health endpoint.
    Returns: {"status": "online", "service": "HR Policies RAG API"}
    """
    return {
        "status": "online",
        "service": "HR Policies RAG API",
    }


@app.get("/version", tags=["Root"])
@app.get("/api/version", tags=["Root"])
async def version():
    return {
        "version": "1.0.0",
        "service": "HR Policies RAG API",
    }


@app.get("/", tags=["Root"])
@app.get("/api", tags=["Root"])
async def root():
    return {
        "status": "online",
        "service": "HR Policies RAG API",
        "docs": "/docs",
        "health": "/health",
    }


# ==========================================================
# 💬 Phase 5: RAG Chat Endpoint
# ==========================================================
@app.post("/ask", response_model=QueryResponse, tags=["Chat"])
@app.post("/api/ask", response_model=QueryResponse, tags=["Chat"])
@app.post("/api/chat", response_model=QueryResponse, tags=["Chat"])
async def ask_question(payload: QueryRequest):
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    rag_req = RAGRequest(
        query=payload.query.strip(),
        top_k=payload.top_k or 5,
        score_threshold=payload.score_threshold if payload.score_threshold is not None else 0.35,
    )

    try:
        res = await ai_service.answer_rag(rag_req)
        source_names = [f"Source: {d.id} ({getattr(d, 'source', 'HR Policy')})" for d in res.sources]
        return QueryResponse(
            query=res.query,
            answer=res.answer,
            status="success",
            sources=source_names,
            matches_count=len(res.sources),
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")


# Safely include extra API routers if available
try:
    from app.api.v1.api import api_router
    app.include_router(api_router, prefix="/api/v1")
except Exception:
    pass

# Export ASGI handler
handler = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
