from loguru import logger

from app.components.clinical.model_trainer import ClinicalModelTrainer
from app.config.configuration import ConfigurationManager

STAGE_NAME = "Clinical Model Training"


def run():
    logger.info(f">>> stage 04: {STAGE_NAME} started")
    manager = ConfigurationManager()
    ClinicalModelTrainer(
        manager.get_clinical_model_trainer_config(),
        manager.get_clinical_transformation_config(),
    ).train()
    logger.info(f">>> stage 04: {STAGE_NAME} complete")


if __name__ == "__main__":
    run()
