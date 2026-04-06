import os
from pathlib import Path

CONFIG_FILE_PATH = Path("config/config.yaml")
PARAMS_FILE_PATH = Path("config/params.yaml")
SCHEMA_FILE_PATH = Path("config/schema.yaml")

def _get_base_dir() -> str:
    return os.environ.get("RETINAXAI_BASE_DIR", "/home/louay/RetinaXAI")

def _resolve_path(relative: str) -> Path:
    base = Path(_get_base_dir())
    return base / relative

SHARED_MODELS_DIR = _resolve_path("shared/models")
SHARED_IMAGING_DIR = _resolve_path("shared/models/imaging")
SHARED_CLINICAL_DIR = _resolve_path("shared/models/clinical")
SHARED_MONITORING_DIR = _resolve_path("shared/models/monitoring")

IMAGING_ARTIFACTS_DIR = Path("artifacts/model/imaging")
CLINICAL_ARTIFACTS_DIR = Path("artifacts/model/clinical")
IMAGING_DATA_DIR = Path("artifacts/data/processed/imaging")
CLINICAL_DATA_DIR = Path("artifacts/data/processed/clinical")
MONITORING_DIR = Path("artifacts/monitoring")