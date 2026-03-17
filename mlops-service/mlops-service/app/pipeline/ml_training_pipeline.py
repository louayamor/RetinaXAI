from loguru import logger

from app.components.data_ingestion import DataIngestion
from app.components.ml_preprocessing import MLPreprocessing
from app.components.ml_model_trainer import MLModelTrainer
from app.components.ml_model_evaluation import MLModelEvaluation
from app.config.configuration import ConfigurationManager


STAGE_1 = "Data Ingestion"
STAGE_2 = "ML Preprocessing"
STAGE_3 = "ML Model Training"
STAGE_4 = "ML Model Evaluation"


class MLTrainingPipeline:
    def __init__(self, manager: ConfigurationManager):
        self.manager = manager

    def run_stage_1(self):
        logger.info(f">>> ml stage: {STAGE_1} started")
        cfg = self.manager.get_data_ingestion_config()
        DataIngestion(cfg).run()
        logger.info(f">>> ml stage: {STAGE_1} complete")

    def run_stage_2(self):
        logger.info(f">>> ml stage: {STAGE_2} started")
        cfg = self.manager.get_preprocessing_config()
        MLPreprocessing(cfg.ml).run()
        logger.info(f">>> ml stage: {STAGE_2} complete")

    def run_stage_3(self):
        logger.info(f">>> ml stage: {STAGE_3} started")
        cfg = self.manager.get_ml_model_trainer_config()
        prep_cfg = self.manager.get_preprocessing_config()
        MLModelTrainer(cfg, prep_cfg.ml).train()
        logger.info(f">>> ml stage: {STAGE_3} complete")

    def run_stage_4(self):
        logger.info(f">>> ml stage: {STAGE_4} started")
        cfg = self.manager.get_ml_model_evaluation_config()
        MLModelEvaluation(cfg).evaluate()
        logger.info(f">>> ml stage: {STAGE_4} complete")

    def run(self):
        self.run_stage_1()
        self.run_stage_2()
        self.run_stage_3()
        self.run_stage_4()