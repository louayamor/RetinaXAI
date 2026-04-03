from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RetinaXAI LLMOps Service"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8002

    backend_service_url: str = "http://backend-service:8000"
    timeout_seconds: int = 60

    SHARED_DIR: Path = Path("/home/louay/RetinaXAI/shared")
    OUTPUT_DIR: Path = Path("/home/louay/RetinaXAI/shared/outputs")
    GRADCAM_DIR: Path = Path("/home/louay/RetinaXAI/shared/outputs/gradcam")
    ARTIFACT_DIR: Path = Path("/home/louay/RetinaXAI/shared/artifacts")

    chroma_path: Path = Path("/home/louay/RetinaXAI/shared/artifacts/chroma")
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    prometheus_metrics_port: int = 9092

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
