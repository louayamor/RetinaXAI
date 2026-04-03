from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RetinaXAI MLOps Service"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8001

    mlflow_tracking_uri: str = ""
    mlflow_tracking_username: str = ""
    mlflow_tracking_password: str = ""

    llmops_service_url: str = "http://llmops-service:8002"
    backend_service_url: str = "http://backend-service:8000"
    timeout_seconds: int = 30

    SHARED_DIR: Path = Path("/home/louay/RetinaXAI/shared")
    UPLOAD_DIR: Path = Path("/home/louay/RetinaXAI/shared/uploads")
    FUNDUS_DIR: Path = Path("/home/louay/RetinaXAI/shared/uploads/fundus")
    OCT_DIR: Path = Path("/home/louay/RetinaXAI/shared/uploads/oct")
    OUTPUT_DIR: Path = Path("/home/louay/RetinaXAI/shared/outputs")
    GRADCAM_DIR: Path = Path("/home/louay/RetinaXAI/shared/outputs/gradcam")
    MODEL_DIR: Path = Path("/home/louay/RetinaXAI/shared/models")
    ARTIFACT_DIR: Path = Path("/home/louay/RetinaXAI/shared/artifacts")

    imaging_model_path: Path = Path("/home/louay/RetinaXAI/shared/models/imaging/model.pth")
    clinical_model_path: Path = Path("/home/louay/RetinaXAI/shared/models/clinical/model.pkl")
    clinical_feature_importance_path: Path = Path("/home/louay/RetinaXAI/shared/models/clinical/feature_importance.json")

    prometheus_metrics_port: int = 9091

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
