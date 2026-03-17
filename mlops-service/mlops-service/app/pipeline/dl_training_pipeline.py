from loguru import logger

from app.components.data_ingestion import DataIngestion
from app.components.preprocessing import DLPreprocessing
from app.components.model_trainer import DLModelTrainer
from app.components.model_evaluation import DLModelEvaluation
from app.config.configuration import ConfigurationManager


STAGE_1 = "Data Ingestion"
STAGE_2 = "DL Preprocessing"
STAGE_3 = "DL Model Training"
STAGE_4 = "DL Model Evaluation"


class DLTrainingPipeline:
    def __init__(self, manager: ConfigurationManager):
        self.manager = manager

    def run_stage_1(self):
        logger.info(f">>> dl stage: {STAGE_1} started")
        cfg = self.manager.get_data_ingestion_config()
        DataIngestion(cfg).run()
        logger.info(f">>> dl stage: {STAGE_1} complete")

    def run_stage_2(self):
        logger.info(f">>> dl stage: {STAGE_2} started")
        cfg = self.manager.get_preprocessing_config()
        DLPreprocessing(cfg.dl).run()
        logger.info(f">>> dl stage: {STAGE_2} complete")

    def run_stage_3(self):
        logger.info(f">>> dl stage: {STAGE_3} started")
        cfg = self.manager.get_dl_model_trainer_config()
        prep_cfg = self.manager.get_preprocessing_config()
        DLModelTrainer(cfg, prep_cfg.dl).train()
        logger.info(f">>> dl stage: {STAGE_3} complete")

    def run_stage_4(self):
        logger.info(f">>> dl stage: {STAGE_4} started")
        cfg = self.manager.get_dl_model_evaluation_config()
        DLModelEvaluation(cfg).evaluate()
        logger.info(f">>> dl stage: {STAGE_4} complete")

    def run(self):
        self.run_stage_1()
        self.run_stage_2()
        self.run_stage_3()
        self.run_stage_4()