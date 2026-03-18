from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.model_evaluation import ClinicalModelEvaluation


def run():
    logger.info(">>> stage 05: clinical model evaluation started")
    manager = ConfigurationManager()
    ClinicalModelEvaluation(manager.get_clinical_model_evaluation_config()).evaluate()
    logger.info(">>> stage 05: clinical model evaluation complete")


if __name__ == "__main__":
    run()
