import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


def _get_base_dir() -> str:
    """Get base directory from environment or fallback to default."""
    return os.environ.get("RETINAXAI_BASE_DIR", "/home/louay/RetinaXAI")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_NAME: str = "retinaxai-backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://retinaxai:retinaxai_secret@localhost:5432/retinaxai"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Storage paths - backend owns its own local workspace
    DATA_DIR: Path = Path()
    UPLOAD_DIR: Path = Path()
    FUNDUS_DIR: Path = Path()
    OCT_DIR: Path = Path()
    OUTPUT_DIR: Path = Path()
    GRADCAM_DIR: Path = Path()
    IMAGING_METRICS: Path = Path()
    CLINICAL_METRICS: Path = Path()

    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ML Service
    ML_SERVICE_URL: str = "http://localhost:8001"
    ML_SERVICE_TIMEOUT: int = 30
    ML_SERVICE_API_KEY: str = "dev-api-key"

    # LLM Service
    LLM_SERVICE_URL: str = "http://localhost:8002"
    LLM_SERVICE_TIMEOUT: int = 60
    LLM_SERVICE_API_KEY: str = "dev-api-key"
    LLM_MODEL: str = "gpt-4o"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    def ensure_dirs(self) -> None:
        for dir_path in [self.FUNDUS_DIR, self.OCT_DIR, self.GRADCAM_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
