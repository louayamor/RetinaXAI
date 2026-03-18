from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.data_transformation import ImagingDataTransformation


def run():
    logger.info(">>> stage 03: imaging data transformation started")
    manager = ConfigurationManager()
    ImagingDataTransformation(manager.get_imaging_transformation_config()).run()
    logger.info(">>> stage 03: imaging data transformation complete")


if __name__ == "__main__":
    run()
