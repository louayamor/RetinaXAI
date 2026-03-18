from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.model_evaluation import ImagingModelEvaluation


def run():
    logger.info(">>> stage 05: imaging model evaluation started")
    manager = ConfigurationManager()
    ImagingModelEvaluation(manager.get_imaging_model_evaluation_config()).evaluate()
    logger.info(">>> stage 05: imaging model evaluation complete")


if __name__ == "__main__":
    run()
