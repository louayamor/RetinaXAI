from pathlib import Path

from app.config.settings import settings

CONFIG_FILE_PATH = Path("config/config.yaml")
PARAMS_FILE_PATH = Path("config/params.yaml")
SCHEMA_FILE_PATH = Path("config/schema.yaml")

DATA_MODELS_DIR = settings.model_dir
IMAGING_MODELS_DIR = settings.model_dir / "imaging"
CLINICAL_MODELS_DIR = settings.model_dir / "clinical"
MONITORING_DIR = settings.monitoring_dir

IMAGING_ARTIFACTS_DIR = settings.imaging_artifacts_dir
CLINICAL_ARTIFACTS_DIR = settings.clinical_artifacts_dir
IMAGING_DATA_DIR = settings.imaging_data_dir
CLINICAL_DATA_DIR = settings.clinical_data_dir
