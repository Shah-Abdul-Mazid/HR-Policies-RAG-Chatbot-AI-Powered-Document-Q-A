from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Full-Stack AI & ML Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Auth / Security
    SECRET_KEY: str = "change_this_to_a_super_secret_key_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # GenAI / LLM Settings
    OPENAI_API_KEY: str = "sk-placeholder-replace-with-real-key"
    LLM_MODEL: str = "llama3.1:latest"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Ollama Settings (Default)
    USE_OLLAMA: bool = True
    OLLAMA_URL: str = "https://keith-unstarting-microtonally.ngrok-free.dev"
    OLLAMA_LOCAL_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "llama3.1:latest"
    OLLAMA_API_SECRET: Optional[str] = None
    NGROK_AUTH: Optional[str] = None

    # Groq Cloud LLM Backup
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "qwen/qwen3.8-27b"

    # Pinecone Vector DB
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX: str = "hr-policies"
    PINECONE_NAMESPACE: str = "hr-policies"

    # ML / Model Settings
    ML_MODEL_NAME: str = "classifier-v1"
    ML_MODEL_PATH: str = "models/weights.bin"
    DEVICE: str = "cpu"
    MAX_BATCH_SIZE: int = 32

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
