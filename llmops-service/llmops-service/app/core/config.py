import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


def _get_base_dir() -> str:
    """Get base directory from environment or fallback to default."""
    return os.environ.get("RETINAXAI_BASE_DIR", "/home/louay/RetinaXAI")


class LLMProvider(str):
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

    # Storage paths - relative, resolved via RETINAXAI_BASE_DIR
    SHARED_DIR: Path = Path("shared")
    OUTPUT_DIR: Path = Path("shared/outputs")
    GRADCAM_DIR: Path = Path("shared/outputs/gradcam")
    VECTORSTORE_DIR: Path = Path("shared/vectorstore")

    chroma_path: Path = Path("shared/vectorstore/chroma")

    # LLM Configuration
    llm_provider: LLMProvider = LLMProvider.GITHUB
    llm_model: str = "openai/gpt-4.1-mini"
    llm_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
    llm_base_url: Optional[str] = None

    # GitHub AI Inference (Azure)
    github_token: Optional[str] = Field(default=None, validation_alias="GITHUB_ACCESS_TOKEN")
    github_endpoint: str = "https://models.github.ai/inference"

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
        """Resolve relative paths to absolute using RETINAXAI_BASE_DIR env var."""
        base = Path(_get_base_dir())
        
        path_fields = [
            "SHARED_DIR", "OUTPUT_DIR", "GRADCAM_DIR", 
            "VECTORSTORE_DIR", "chroma_path"
        ]
        
        for field in path_fields:
            value = getattr(self, field)
            if value and not Path(value).is_absolute():
                setattr(self, field, base / value)


settings = Settings()