import time
from typing import AsyncGenerator, List
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.schemas.rag import RAGRequest, RAGResponse, DocumentChunk
from app.ai.llm import llm_client
from app.ai.rag import retriever
from app.core.config import settings


class AIService:
    async def chat(self, request: ChatRequest) -> ChatResponse:
        start_time = time.perf_counter()
        response_text = await llm_client.generate_response(request.messages)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ChatResponse(
            message=ChatMessage(role="assistant", content=response_text),
            model=settings.OLLAMA_MODEL if settings.USE_OLLAMA else settings.LLM_MODEL,
            tokens_used=len(response_text.split()),
            latency_ms=round(latency_ms, 2),
        )

    async def stream_chat(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        async for chunk in llm_client.stream_tokens(request.messages):
            yield chunk

    async def answer_rag(self, request: RAGRequest) -> RAGResponse:
        start_time = time.perf_counter()
        docs = retriever.search(request.query, top_k=request.top_k)
        
        if docs:
            context = "\n\n".join([f"[{i+1}] {d.text}" for i, d in enumerate(docs)])
            prompt = (
                "You are a helpful and concise HR policy assistant. "
                "Answer the question using the provided HR context.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {request.query}\n\n"
                "Answer:"
            )
        else:
            prompt = f"You are a concise HR policy assistant. Answer this question: {request.query}"

        # 1. Primary: Ollama
        answer = None
        if settings.USE_OLLAMA:
            answer = await llm_client.call_ollama(prompt)

        # 2. Backup: Groq
        if not answer:
            answer = await llm_client.call_groq(prompt)

        # 3. Fallback to context
        if not answer:
            if docs:
                answer = "Here is the relevant information found in the policy documents:\n\n" + "\n\n".join([d.text for d in docs])
            else:
                answer = f"I couldn't find specific HR information for: '{request.query}'."

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return RAGResponse(
            query=request.query,
            answer=answer,
            sources=docs,
            latency_ms=round(latency_ms, 2),
        )


ai_service = AIService()
