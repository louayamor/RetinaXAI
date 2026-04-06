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

    shared_dir: Path = Path("/home/louay/RetinaXAI/shared")
    upload_dir: Path = Path("/home/louay/RetinaXAI/shared/uploads")
    fundus_dir: Path = Path("/home/louay/RetinaXAI/shared/uploads/fundus")
    oct_dir: Path = Path("/home/louay/RetinaXAI/shared/uploads/oct")
    output_dir: Path = Path("/home/louay/RetinaXAI/shared/outputs")
    gradcam_dir: Path = Path("/home/louay/RetinaXAI/shared/outputs/gradcam")
    model_dir: Path = Path("/home/louay/RetinaXAI/shared/models")
    vectorstore_dir: Path = Path("/home/louay/RetinaXAI/shared/vectorstore")

    imaging_model_path: Path = Path("/home/louay/RetinaXAI/shared/models/imaging/model.pth")
    clinical_model_path: Path = Path("/home/louay/RetinaXAI/shared/models/clinical/model.pkl")
    clinical_feature_importance_path: Path = Path("/home/louay/RetinaXAI/shared/models/clinical/feature_importance.json")

    imaging_metrics_path: Path = Path("artifacts/model/imaging/metrics.json")
    clinical_metrics_path: Path = Path("artifacts/model/clinical/metrics.json")

    prometheus_metrics_port: int = 9091

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
