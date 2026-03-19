from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "RetinaXAI MLOps Service"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    mlflow_tracking_uri: str = ""
    mlflow_tracking_username: str = ""
    mlflow_tracking_password: str = ""

    llmops_service_url: str = "http://llmops-service:8001"
    timeout_seconds: int = 30

    imaging_model_path: Path = Path("artifacts/model/imaging/model.pth")
    clinical_model_path: Path = Path("artifacts/model/clinical/model.pkl")
    clinical_feature_importance_path: Path = Path("artifacts/model/clinical/feature_importance.json")
    imaging_metrics_path: Path = Path("artifacts/model/imaging/metrics.json")
    clinical_metrics_path: Path = Path("artifacts/model/clinical/metrics.json")

    prometheus_metrics_port: int = 9090

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
