from loguru import logger
from app.config.configuration import ConfigurationManager
from app.pipeline.imaging.stage_01_data_ingestion import run as imaging_ingest
from app.pipeline.imaging.stage_02_data_cleaning import run as imaging_clean
from app.pipeline.imaging.stage_03_data_transformation import run as imaging_transform
from app.pipeline.imaging.stage_04_model_trainer import run as imaging_train
from app.pipeline.imaging.stage_05_model_evaluation import run as imaging_evaluate
from app.pipeline.clinical.stage_01_data_ingestion import run as clinical_ingest
from app.pipeline.clinical.stage_02_data_cleaning import run as clinical_clean
from app.pipeline.clinical.stage_03_data_transformation import run as clinical_transform
from app.pipeline.clinical.stage_04_model_trainer import run as clinical_train
from app.pipeline.clinical.stage_05_model_evaluation import run as clinical_evaluate


class TrainingPipeline:
    def run_imaging(self):
        logger.info("=== imaging pipeline started ===")
        imaging_ingest()
        imaging_clean()
        imaging_transform()
        imaging_train()
        imaging_evaluate()
        logger.info("=== imaging pipeline complete ===")

    def run_clinical(self):
        logger.info("=== clinical pipeline started ===")
        clinical_ingest()
        clinical_clean()
        clinical_transform()
        clinical_train()
        clinical_evaluate()
        logger.info("=== clinical pipeline complete ===")

    def run(self):
        logger.info("=== unified training pipeline started ===")
        self.run_imaging()
        self.run_clinical()
        logger.info("=== unified training pipeline complete ===")
