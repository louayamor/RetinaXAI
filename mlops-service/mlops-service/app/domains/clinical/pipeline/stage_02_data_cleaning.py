from loguru import logger

from app.domains.clinical.components.data_cleaning import ClinicalDataCleaning
from app.config.configuration import ConfigurationManager

STAGE_NAME = "Clinical Data Cleaning"


def run():
    logger.info(f">>> stage 02: {STAGE_NAME} started")
    manager = ConfigurationManager()
    ClinicalDataCleaning(manager.get_clinical_cleaning_config()).run()
    logger.info(f">>> stage 02: {STAGE_NAME} complete")


if __name__ == "__main__":
    run()
