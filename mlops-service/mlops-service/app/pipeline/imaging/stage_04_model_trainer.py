from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.model_trainer import ImagingModelTrainer


def run():
    logger.info(">>> stage 04: imaging model training started")
    manager = ConfigurationManager()
    cfg = manager.get_imaging_model_trainer_config()
    transformation_cfg = manager.get_imaging_transformation_config()
    ImagingModelTrainer(cfg, transformation_cfg).train()
    logger.info(">>> stage 04: imaging model training complete")


if __name__ == "__main__":
    run()
