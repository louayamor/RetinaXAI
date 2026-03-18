from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.model_trainer import ClinicalModelTrainer


def run():
    logger.info(">>> stage 04: clinical model training started")
    manager = ConfigurationManager()
    cfg = manager.get_clinical_model_trainer_config()
    transformation_cfg = manager.get_clinical_transformation_config()
    ClinicalModelTrainer(cfg, transformation_cfg).train()
    logger.info(">>> stage 04: clinical model training complete")


if __name__ == "__main__":
    run()
