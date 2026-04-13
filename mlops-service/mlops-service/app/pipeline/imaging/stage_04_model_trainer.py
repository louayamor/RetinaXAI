from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.model_trainer import ImagingModelTrainer


def run():
    logger.info(">>> stage 04: imaging model training started")
    manager = ConfigurationManager()
    cfg = manager.get_imaging_model_trainer_config()
    transformation_cfg = manager.get_imaging_transformation_config()
    logger.info(
        f"stage 04 config: model={cfg.model_name}, pretrained={cfg.pretrained}, checkpoint={cfg.checkpoint_path}, train_csv={transformation_cfg.train_csv}, test_csv={transformation_cfg.test_csv}"
    )
    ImagingModelTrainer(cfg, transformation_cfg).train()
    logger.info(">>> stage 04: imaging model training complete")


if __name__ == "__main__":
    run()
