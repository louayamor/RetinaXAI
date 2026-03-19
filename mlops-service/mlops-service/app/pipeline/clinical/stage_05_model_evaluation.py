from loguru import logger

from app.components.clinical.model_evaluation import ClinicalModelEvaluation
from app.config.configuration import ConfigurationManager

STAGE_NAME = "Clinical Model Evaluation"


def run():
    logger.info(f">>> stage 05: {STAGE_NAME} started")
    manager = ConfigurationManager()
    ClinicalModelEvaluation(manager.get_clinical_model_evaluation_config()).evaluate()
    logger.info(f">>> stage 05: {STAGE_NAME} complete")


if __name__ == "__main__":
    run()