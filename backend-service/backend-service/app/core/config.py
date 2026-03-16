from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_NAME: str = "healthcare-backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    UPLOAD_DIR: str = "uploads/mri"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ML_SERVICE_URL: str
    ML_SERVICE_TIMEOUT: int = 30
    ML_SERVICE_API_KEY: str

    LLM_SERVICE_URL: str
    LLM_SERVICE_TIMEOUT: int = 60
    LLM_SERVICE_API_KEY: str
    LLM_MODEL: str = "gpt-4o"

    CORS_ORIGINS: List[str] = []

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()