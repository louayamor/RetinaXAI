import os
from pathlib import Path

from app.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from app.entity.config_entity import (
    DataIngestionConfig,
    DLModelEvaluationConfig,
    DLModelTrainerConfig,
    DLMonitoringConfig,
    DLPreprocessingConfig,
    HuggingFaceIngestionConfig,
    MLModelEvaluationConfig,
    MLModelTrainerConfig,
    MLMonitoringConfig,
    MLPreprocessingConfig,
    MonitoringConfig,
    PreprocessingConfig,
    SamayaIngestionConfig,
)
from app.utils.common import create_directories, read_yaml


class ConfigurationManager:
    def __init__(
        self,
        config_path: Path = CONFIG_FILE_PATH,
        params_path: Path = PARAMS_FILE_PATH,
        schema_path: Path = SCHEMA_FILE_PATH,
    ):
        self.config = read_yaml(config_path)
        self.params = read_yaml(params_path)
        self.schema = read_yaml(schema_path)
        create_directories([Path(self.config.artifacts_root)])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        cfg = self.config.data_ingestion
        create_directories([Path(cfg.root_dir)])
        return DataIngestionConfig(
            root_dir=Path(cfg.root_dir),
            huggingface=HuggingFaceIngestionConfig(
                root_dir=Path(cfg.root_dir),
                dataset_name=cfg.huggingface.dataset_name,
                train_split=cfg.huggingface.train_split,
                test_split=cfg.huggingface.test_split,
                max_samples=cfg.huggingface.get("max_samples", None),
            ),
            samaya=SamayaIngestionConfig(
                images_dir=Path(cfg.samaya.images_dir),
                reports_csv=Path(cfg.samaya.reports_csv),
                reports_json=Path(cfg.samaya.reports_json),
            ),
        )

    def get_preprocessing_config(self) -> PreprocessingConfig:
        cfg = self.config.preprocessing
        create_directories([
            Path(cfg.root_dir),
            Path(cfg.dl.train_csv).parent,
            Path(cfg.ml.train_csv).parent,
        ])
        return PreprocessingConfig(
            root_dir=Path(cfg.root_dir),
            dl=DLPreprocessingConfig(
                root_dir=Path(cfg.root_dir),
                source_dir=Path(cfg.dl.source_dir),
                image_size=cfg.dl.image_size,
                train_csv=Path(cfg.dl.train_csv),
                test_csv=Path(cfg.dl.test_csv),
                samaya_csv=Path(cfg.dl.samaya_csv),
            ),
            ml=MLPreprocessingConfig(
                root_dir=Path(cfg.root_dir),
                source_csv=Path(cfg.ml.source_csv),
                train_csv=Path(cfg.ml.train_csv),
                test_csv=Path(cfg.ml.test_csv),
                feature_file=Path(cfg.ml.feature_file),
            ),
        )

    def get_dl_model_trainer_config(self) -> DLModelTrainerConfig:
        cfg = self.config.dl_model
        create_directories([Path(cfg.root_dir)])
        return DLModelTrainerConfig(
            root_dir=Path(cfg.root_dir),
            model_name=cfg.model_name,
            pretrained=cfg.pretrained,
            checkpoint_path=Path(cfg.checkpoint_path),
            finetuned_checkpoint_path=Path(cfg.finetuned_checkpoint_path),
        )

    def get_ml_model_trainer_config(self) -> MLModelTrainerConfig:
        cfg = self.config.ml_model
        create_directories([Path(cfg.root_dir)])
        return MLModelTrainerConfig(
            root_dir=Path(cfg.root_dir),
            model_name=cfg.model_name,
            checkpoint_path=Path(cfg.checkpoint_path),
            feature_importance_path=Path(cfg.feature_importance_path),
        )

    def get_dl_model_evaluation_config(self) -> DLModelEvaluationConfig:
        cfg = self.config.model_evaluation.dl
        mlflow_cfg = self.config.mlflow
        create_directories([Path(cfg.root_dir)])
        return DLModelEvaluationConfig(
            root_dir=Path(cfg.root_dir),
            test_csv=Path(cfg.test_csv),
            model_path=Path(cfg.model_path),
            finetuned_model_path=Path(cfg.finetuned_model_path),
            metric_file=Path(cfg.metric_file),
            finetuned_metric_file=Path(cfg.finetuned_metric_file),
            mlflow_uri=os.environ.get("MLFLOW_TRACKING_URI", ""),
            experiment_name=mlflow_cfg.experiment_name,
            run_name=mlflow_cfg.dl_run_name,
        )

    def get_ml_model_evaluation_config(self) -> MLModelEvaluationConfig:
        cfg = self.config.model_evaluation.ml
        mlflow_cfg = self.config.mlflow
        create_directories([Path(cfg.root_dir)])
        return MLModelEvaluationConfig(
            root_dir=Path(cfg.root_dir),
            test_csv=Path(cfg.test_csv),
            model_path=Path(cfg.model_path),
            metric_file=Path(cfg.metric_file),
            mlflow_uri=os.environ.get("MLFLOW_TRACKING_URI", ""),
            experiment_name=mlflow_cfg.experiment_name,
            run_name=mlflow_cfg.ml_run_name,
        )

    def get_monitoring_config(self) -> MonitoringConfig:
        cfg = self.config.monitoring
        create_directories([Path(cfg.reports_dir)])
        return MonitoringConfig(
            reports_dir=Path(cfg.reports_dir),
            dl=DLMonitoringConfig(
                reports_dir=Path(cfg.reports_dir),
                drift_report=Path(cfg.dl.drift_report),
                classification_report=Path(cfg.dl.classification_report),
                reference_csv=Path(cfg.dl.reference_csv),
                current_csv=Path(cfg.dl.current_csv),
            ),
            ml=MLMonitoringConfig(
                reports_dir=Path(cfg.reports_dir),
                drift_report=Path(cfg.ml.drift_report),
                classification_report=Path(cfg.ml.classification_report),
                reference_csv=Path(cfg.ml.reference_csv),
                current_csv=Path(cfg.ml.current_csv),
            ),
            prometheus_port=cfg.prometheus_port,
        )