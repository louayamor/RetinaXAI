import os
from pathlib import Path

from pydantic_settings import BaseSettings


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

    # Paths - use relative paths, resolved to absolute at runtime
    # Override individual paths with env vars (e.g., SHARED_DIR, MODEL_DIR)
    # Or set RETINAXAI_BASE_DIR to change the base for all paths
    shared_dir: Path = Path("shared")
    upload_dir: Path = Path("shared/uploads")
    fundus_dir: Path = Path("shared/uploads/fundus")
    oct_dir: Path = Path("shared/uploads/oct")
    output_dir: Path = Path("shared/outputs")
    gradcam_dir: Path = Path("shared/outputs/gradcam")
    model_dir: Path = Path("shared/models")
    vectorstore_dir: Path = Path("shared/vectorstore")

    imaging_model_path: Path = Path("shared/models/imaging/model.pth")
    clinical_model_path: Path = Path("shared/models/clinical/model.pkl")
    clinical_feature_importance_path: Path = Path("shared/models/clinical/feature_importance.json")

    imaging_metrics_path: Path = Path("artifacts/model/imaging/metrics.json")
    clinical_metrics_path: Path = Path("artifacts/model/clinical/metrics.json")

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
            "shared_dir", "upload_dir", "fundus_dir", "oct_dir", 
            "output_dir", "gradcam_dir", "model_dir", "vectorstore_dir",
            "imaging_model_path", "clinical_model_path", 
            "clinical_feature_importance_path"
        ]
        
        for field in path_fields:
            value = getattr(self, field)
            if value and not Path(value).is_absolute():
                setattr(self, field, base / value)


settings = Settings()