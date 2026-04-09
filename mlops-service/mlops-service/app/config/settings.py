import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


def _get_base_dir() -> str:
    """Get base directory from environment or fallback to default."""
    return os.environ.get("RETINAXAI_BASE_DIR", "/home/louay/RetinaXAI")


class Settings(BaseSettings):
    app_name: str = "RetinaXAI MLOps Service"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8001

    # MLflow / DagsHub
    mlflow_tracking_uri: str = ""
    mlflow_tracking_username: str = ""
    mlflow_tracking_password: str = ""

    # Inter-service URLs
    llmops_service_url: str = "http://llmops-service:8002"
    backend_service_url: str = "http://backend-service:8000"
    timeout_seconds: int = 30

    # Paths are injected via .env as absolute service-local locations.
    data_dir: Path = Path()
    upload_dir: Path = Path()
    fundus_dir: Path = Path()
    oct_dir: Path = Path()
    output_dir: Path = Path()
    gradcam_dir: Path = Path()
    model_dir: Path = Path()
    vectorstore_dir: Path = Path()

    imaging_model_path: Path = Path()
    clinical_model_path: Path = Path()
    clinical_feature_importance_path: Path = Path()

    imaging_metrics_path: Path = Path()
    clinical_metrics_path: Path = Path()

    artifacts_root: Path = Path()
    imaging_artifacts_dir: Path = Path()
    clinical_artifacts_dir: Path = Path()
    imaging_data_dir: Path = Path()
    clinical_data_dir: Path = Path()
    monitoring_dir: Path = Path()
    training_jobs_file: Path = Path()
    ocr_input_dir: Path = Path()
    ocr_output_dir: Path = Path()

    prometheus_metrics_port: int = 9091

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
            "data_dir", "upload_dir", "fundus_dir", "oct_dir", 
            "output_dir", "gradcam_dir", "model_dir", "vectorstore_dir",
            "imaging_model_path", "clinical_model_path", 
            "clinical_feature_importance_path", "ocr_output_dir"
        ]
        
        for field in path_fields:
            value = getattr(self, field)
            if value and not Path(value).is_absolute():
                setattr(self, field, base / value)


settings = Settings()
