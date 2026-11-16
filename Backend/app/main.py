from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.core.config import settings
from app.api.v1.api import api_router
from app.ml.model import ml_model
from app.services.ai_service import ai_service
from app.schemas.rag import RAGRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Safe startup for serverless
    try:
        print(f"\n🚀 Initializing AI & ML Engine...")
        print(f"🧠 Primary LLM: '{settings.OLLAMA_MODEL}' (Ollama default: {settings.USE_OLLAMA})")
        ml_model.load()
        print(f"✅ AI LLM & RAG Engine Ready.\n")
    except Exception as e:
        print(f"⚠️ Startup warning: {e}")
    yield
    try:
        print("🔻 Unloading AI/ML models...")
        ml_model.unload()
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Full-stack FastAPI service combining enterprise web API patterns "
        "with production AI, RAG, and Ollama integration."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Enable CORS for local dev and Vercel production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# ==========================================================
# 🔌 Direct Frontend Compatibility Routes (/api/ask, /api/health)
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


def _health_payload():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "llm_provider": f"Ollama ({settings.OLLAMA_MODEL})" if settings.USE_OLLAMA else settings.LLM_MODEL,
        "ollama_enabled": settings.USE_OLLAMA,
        "device": settings.DEVICE,
    }


@app.get("/", tags=["Root"])
@app.get("/api", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "health": _health_payload(),
        "endpoints": {
            "POST /api/ask": "Submit HR question",
            "GET /api/health": "Health check",
            "GET /version": "API Version",
            "Docs": "/docs",
        },
    }


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    return _health_payload()


@app.get("/version", tags=["Root"])
@app.get("/api/version", tags=["Root"])
async def version_check():
    return {
        "version": "1.0.0",
        "service": settings.PROJECT_NAME,
        "llm_provider": f"Ollama ({settings.OLLAMA_MODEL})" if settings.USE_OLLAMA else settings.LLM_MODEL,
    }


@app.post("/ask", response_model=QueryResponse, tags=["Chat"])
@app.post("/api/ask", response_model=QueryResponse, tags=["Chat"])
async def ask_endpoint(payload: QueryRequest):
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    rag_req = RAGRequest(
        query=payload.query.strip(),
        top_k=payload.top_k or 5,
        score_threshold=payload.score_threshold or 0.35,
    )
    res = await ai_service.answer_rag(rag_req)
    
    source_names = [f"Source #{d.id}" for d in res.sources]
    return QueryResponse(
        query=res.query,
        answer=res.answer,
        status="success",
        sources=source_names,
        matches_count=len(res.sources),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
