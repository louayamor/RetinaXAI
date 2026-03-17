import os
from pathlib import Path
from app.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from app.entity.config_entity import (
    DataIngestionConfig,
    ModelEvaluationConfig,
    ModelTrainerConfig,
    MonitoringConfig,
    PreprocessingConfig,
    OCRPipelineConfig,
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
            dataset_name=cfg.dataset_name,
            train_split=cfg.train_split,
            test_split=cfg.test_split,
            shared_uploads_dir=Path(cfg.shared_uploads_dir),
        )

    def get_preprocessing_config(self) -> PreprocessingConfig:
        cfg = self.config.preprocessing
        create_directories([Path(cfg.root_dir)])
        return PreprocessingConfig(
            root_dir=Path(cfg.root_dir),
            source_dir=Path(cfg.source_dir),
            image_size=cfg.image_size,
            train_csv=Path(cfg.train_csv),
            test_csv=Path(cfg.test_csv),
        )

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        cfg = self.config.model_trainer
        create_directories([Path(cfg.root_dir)])
        return ModelTrainerConfig(
            root_dir=Path(cfg.root_dir),
            model_name=cfg.model_name,
            pretrained=cfg.pretrained,
            checkpoint_path=Path(cfg.checkpoint_path),
        )

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        cfg = self.config.model_evaluation
        mlflow_cfg = self.config.mlflow
        mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI", "")
        create_directories([Path(cfg.root_dir)])
        return ModelEvaluationConfig(
            root_dir=Path(cfg.root_dir),
            test_csv=Path(cfg.test_csv),
            model_path=Path(cfg.model_path),
            metric_file=Path(cfg.metric_file),
            mlflow_uri=mlflow_uri,
            experiment_name=mlflow_cfg.experiment_name,
            run_name=mlflow_cfg.run_name,
        )

    def get_monitoring_config(self) -> MonitoringConfig:
        cfg = self.config.monitoring
        create_directories([Path(cfg.reports_dir)])
        return MonitoringConfig(
            reports_dir=Path(cfg.reports_dir),
            drift_report=Path(cfg.drift_report),
            classification_report=Path(cfg.classification_report),
            reference_csv=Path(cfg.reference_csv),
            current_csv=Path(cfg.current_csv),
            prometheus_port=cfg.prometheus_port,
        )

    def get_ocr_pipeline_config(self) -> OCRPipelineConfig:
        cfg = self.config.ocr_pipeline
        create_directories([
            Path(cfg.root_dir),
            Path(cfg.output_dir),
            Path(cfg.images_dir),
        ])
        return OCRPipelineConfig(
            root_dir=Path(cfg.root_dir),
            input_dir=Path(cfg.input_dir),
            output_dir=Path(cfg.output_dir),
            images_dir=Path(cfg.images_dir),
            json_output=Path(cfg.json_output),
            csv_output=Path(cfg.csv_output),
            regions_config=Path(cfg.regions_config),
        )
