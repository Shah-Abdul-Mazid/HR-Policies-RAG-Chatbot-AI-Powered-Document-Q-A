from pydantic import BaseModel
from typing import List, Optional


class DocumentChunk(BaseModel):
    id: str
    text: str
    score: float
    source: Optional[str] = "HR Policy Document"


class RAGRequest(BaseModel):
    query: str
    top_k: int = 3
    score_threshold: Optional[float] = 0.35


class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: List[DocumentChunk]
    latency_ms: float
