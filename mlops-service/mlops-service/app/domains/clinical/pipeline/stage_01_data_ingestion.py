from loguru import logger
from app.config.configuration import ConfigurationManager
from app.domains.clinical.components.data_ingestion import ClinicalDataIngestion


def run():
    logger.info(">>> stage 01: clinical data ingestion started")
    manager = ConfigurationManager()
    ClinicalDataIngestion(manager.get_clinical_ingestion_config()).run()
    logger.info(">>> stage 01: clinical data ingestion complete")


if __name__ == "__main__":
    run()
