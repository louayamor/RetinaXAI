from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.data_ingestion import ClinicalDataIngestion
from app.components.clinical.data_cleaning import ClinicalDataCleaning


def run():
    logger.info(">>> stage 02: clinical data cleaning started")
    manager = ConfigurationManager()
    df = ClinicalDataIngestion(manager.get_clinical_ingestion_config()).run()
    ClinicalDataCleaning(manager.get_clinical_cleaning_config()).run(df)
    logger.info(">>> stage 02: clinical data cleaning complete")


if __name__ == "__main__":
    run()
