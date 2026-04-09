import os
from enum import StrEnum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


def _get_base_dir() -> str:
    """Get base directory from environment or fallback to default."""
    return os.environ.get("RETINAXAI_BASE_DIR", "/home/louay/RetinaXAI")


class LLMProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GITHUB = "github"
    MOCK = "mock"


class Settings(BaseSettings):
    app_name: str = "RetinaXAI LLMOps Service"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8002

    # Inter-service
    backend_service_url: str = "http://backend-service:8000"
    timeout_seconds: int = 60
    rag_manifest_url: str = "http://mlops-service:8001/api/rag/manifest"

    # Local storage only; LLMOps receives context from backend.
    DATA_DIR: Path = Path()
    CACHE_DIR: Path = Path()
    rag_chroma_persist_directory: Path = Path("llmops-service/llmops-service/data/rag/chroma")
    rag_chroma_collection_name: str = "retinaxai_rag"
    rag_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 80

    # LLM Configuration
    llm_provider: LLMProvider = LLMProvider.GITHUB
    llm_model: str = "openai/gpt-4.1-mini"
    llm_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    llm_base_url: Optional[str] = None

    # GitHub AI Inference (Azure)
    github_token: Optional[str] = Field(default=None, validation_alias="GITHUB_ACCESS_TOKEN")
    github_endpoint: str = "https://models.github.ai/inference"

    # DagsHub / MLflow
    mlflow_tracking_uri: str = ""
    mlflow_experiment_name: str = "retinaxai-llmops"

    # Ollama (fallback/local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    prometheus_metrics_port: int = 9092

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def __init__(self, **data):
        super().__init__(**data)
        self._resolve_paths()

    def _resolve_paths(self):
        base = Path(_get_base_dir())
        path_fields = ["DATA_DIR", "CACHE_DIR", "rag_chroma_persist_directory"]
        for field in path_fields:
            value = getattr(self, field)
            if value and not Path(value).is_absolute():
                setattr(self, field, base / value)

settings = Settings()
