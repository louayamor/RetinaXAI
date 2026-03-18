from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.data_ingestion import ImagingDataIngestion


def run():
    logger.info(">>> stage 01: imaging data ingestion started")
    manager = ConfigurationManager()
    ImagingDataIngestion(manager.get_imaging_ingestion_config()).run()
    logger.info(">>> stage 01: imaging data ingestion complete")


if __name__ == "__main__":
    run()
