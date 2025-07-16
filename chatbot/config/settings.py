import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, custom
    api_key: str = os.getenv("LLM_API_KEY", "")
    api_base_url: str = os.getenv("LLM_API_BASE_URL", "")  # For custom/private endpoints
    model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini")
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    
    # RAG Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "3"))
    
    # Vector Database
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", str(Path(__file__).parent.parent / "data" / "vectordb"))
    documents_path: str = os.getenv("DOCUMENTS_PATH", str(Path(__file__).parent.parent / "data" / "documents"))
    
    # Guardrails
    guardrails_config: str = os.getenv("GUARDRAILS_CONFIG", str(Path(__file__).parent / "guardrails.yaml"))
    guardrails_api_key: str = os.getenv("GUARDRAILS_API_KEY", "")
    guardrails_id: str = os.getenv("GUARDRAILS_ID", "")
    
    class Config:
        env_file = ".env"

settings = Settings()