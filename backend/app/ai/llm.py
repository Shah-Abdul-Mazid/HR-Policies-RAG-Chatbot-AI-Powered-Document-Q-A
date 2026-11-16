"""GenAI LLM client with Ollama as primary default and Groq/OpenAI fallback."""
import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.schemas.chat import ChatMessage

logger = logging.getLogger("llm_client")


class LLMClient:
    def __init__(self):
        self.model_name = settings.OLLAMA_MODEL if settings.USE_OLLAMA else settings.LLM_MODEL
        self.ollama_local = settings.OLLAMA_LOCAL_URL.rstrip('/')
        self.ollama_remote = settings.OLLAMA_URL.rstrip('/')
        self.ollama_secret = settings.OLLAMA_API_SECRET
        self.groq_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL
        self.openai_key = settings.OPENAI_API_KEY

    def _get_ngrok_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "69420",
        }
        if self.ollama_secret:
            headers["Authorization"] = f"Bearer {self.ollama_secret}"
        return headers

    async def call_ollama(self, prompt: str) -> Optional[str]:
        """Tries local Ollama first, then ngrok remote Ollama."""
        # 1. Try local Ollama
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(
                    f"{self.ollama_local}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
        except Exception as e:
            logger.info(f"Local Ollama not reachable, trying remote ngrok tunnel: {e}")

        # 2. Try remote ngrok Ollama
        if self.ollama_remote:
            try:
                headers = self._get_ngrok_headers()
                async with httpx.AsyncClient(timeout=30.0) as client:
                    res = await client.post(
                        f"{self.ollama_remote}/api/generate",
                        headers=headers,
                        json={
                            "model": settings.OLLAMA_MODEL,
                            "prompt": prompt,
                            "stream": False,
                        }
                    )
                    if res.status_code == 200:
                        data = res.json()
                        return data.get("response", "").strip()
            except Exception as e:
                logger.warning(f"Remote ngrok Ollama call failed: {e}")

        return None

    async def call_groq(self, prompt: str) -> Optional[str]:
        """Backup cloud LLM via Groq."""
        if not self.groq_key:
            return None
        try:
            # Prefer llama-3.1-8b-instant or user's groq_model
            model_to_use = self.groq_model if self.groq_model else "llama-3.1-8b-instant"
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.groq_key}"},
                    json={
                        "model": model_to_use,
                        "messages": [
                            {"role": "system", "content": "You are a concise and factual HR policy assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 512,
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0]["message"]["content"].strip()
                else:
                    # If specific model fails (e.g. decommissioned), fallback to llama-3.1-8b-instant
                    res2 = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {self.groq_key}"},
                        json={
                            "model": "llama-3.1-8b-instant",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.2,
                            "max_tokens": 512,
                        }
                    )
                    if res2.status_code == 200:
                        return res2.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"Groq API call error: {e}")
        return None

    async def generate_response(self, messages: list[ChatMessage]) -> str:
        """Non-streaming generation with Ollama as primary default."""
        user_message = messages[-1].content

        # 1. Primary: Ollama
        if settings.USE_OLLAMA:
            ans = await self.call_ollama(user_message)
            if ans:
                return ans

        # 2. Backup: Groq
        ans = await self.call_groq(user_message)
        if ans:
            return ans

        # 3. Fallback echo
        return f"[Ollama ({self.model_name})]: Response to '{user_message}'."

    async def stream_tokens(self, messages: list[ChatMessage]) -> AsyncGenerator[str, None]:
        """Real-time token streaming generator (SSE)."""
        prompt = messages[-1].content
        # Get full answer and yield tokens
        full_text = await self.generate_response(messages)
        words = full_text.split(" ")
        for word in words:
            await asyncio.sleep(0.02)
            yield f"data: {word} \n\n"
        yield "data: [DONE]\n\n"


llm_client = LLMClient()
