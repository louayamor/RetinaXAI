from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.data_ingestion import ClinicalDataIngestion
from app.components.clinical.data_cleaning import ClinicalDataCleaning
from app.components.clinical.data_transformation import ClinicalDataTransformation


def run():
    logger.info(">>> stage 03: clinical data transformation started")
    manager = ConfigurationManager()
    df = ClinicalDataIngestion(manager.get_clinical_ingestion_config()).run()
    df = ClinicalDataCleaning(manager.get_clinical_cleaning_config()).run(df)
    ClinicalDataTransformation(manager.get_clinical_transformation_config()).run(df)
    logger.info(">>> stage 03: clinical data transformation complete")


if __name__ == "__main__":
    run()
