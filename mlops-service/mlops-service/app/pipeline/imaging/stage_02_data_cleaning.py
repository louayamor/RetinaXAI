from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.data_cleaning import ImagingDataCleaning


def run():
    logger.info(">>> stage 02: imaging data cleaning started")
    manager = ConfigurationManager()
    ImagingDataCleaning(manager.get_imaging_cleaning_config()).run()
    logger.info(">>> stage 02: imaging data cleaning complete")


if __name__ == "__main__":
    run()
