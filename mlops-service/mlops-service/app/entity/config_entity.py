from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HuggingFaceIngestionConfig:
    root_dir: Path
    dataset_name: str
    train_split: str
    test_split: str


@dataclass(frozen=True)
class SamayaIngestionConfig:
    images_dir: Path
    reports_csv: Path
    reports_json: Path


@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    huggingface: HuggingFaceIngestionConfig
    samaya: SamayaIngestionConfig


@dataclass(frozen=True)
class DLPreprocessingConfig:
    root_dir: Path
    source_dir: Path
    image_size: int
    train_csv: Path
    test_csv: Path
    samaya_csv: Path


@dataclass(frozen=True)
class MLPreprocessingConfig:
    root_dir: Path
    source_csv: Path
    train_csv: Path
    test_csv: Path
    feature_file: Path


@dataclass(frozen=True)
class PreprocessingConfig:
    root_dir: Path
    dl: DLPreprocessingConfig
    ml: MLPreprocessingConfig


@dataclass(frozen=True)
class DLModelTrainerConfig:
    root_dir: Path
    model_name: str
    pretrained: bool
    checkpoint_path: Path


@dataclass(frozen=True)
class MLModelTrainerConfig:
    root_dir: Path
    model_name: str
    checkpoint_path: Path
    feature_importance_path: Path


@dataclass(frozen=True)
class DLModelEvaluationConfig:
    root_dir: Path
    test_csv: Path
    model_path: Path
    metric_file: Path
    mlflow_uri: str
    experiment_name: str
    run_name: str


@dataclass(frozen=True)
class MLModelEvaluationConfig:
    root_dir: Path
    test_csv: Path
    model_path: Path
    metric_file: Path
    mlflow_uri: str
    experiment_name: str
    run_name: str


@dataclass(frozen=True)
class DLMonitoringConfig:
    reports_dir: Path
    drift_report: Path
    classification_report: Path
    reference_csv: Path
    current_csv: Path


@dataclass(frozen=True)
class MLMonitoringConfig:
    reports_dir: Path
    drift_report: Path
    classification_report: Path
    reference_csv: Path
    current_csv: Path


@dataclass(frozen=True)
class MonitoringConfig:
    reports_dir: Path
    dl: DLMonitoringConfig
    ml: MLMonitoringConfig
    prometheus_port: int