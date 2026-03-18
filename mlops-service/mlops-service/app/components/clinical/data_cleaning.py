import pandas as pd
from loguru import logger

from app.entity.config_entity import ClinicalCleaningConfig
from app.utils.common import read_yaml
from app.constants import SCHEMA_FILE_PATH


class ClinicalDataCleaning:
    def __init__(self, config: ClinicalCleaningConfig):
        self.config = config
        self.schema = read_yaml(SCHEMA_FILE_PATH)

    def run(self) -> pd.DataFrame:
        cleaned_csv = self.config.root_dir / "cleaned.csv"
        if cleaned_csv.exists():
            logger.info(f"cleaned CSV already exists, skipping: {cleaned_csv}")
            return pd.read_csv(cleaned_csv)
        
        raw_csv = self.config.root_dir / "raw.csv"
        logger.info(f"loading raw CSV: {raw_csv}")

        df = pd.read_csv(raw_csv)
        original_size = len(df)
        logger.info(f"clinical data cleaning started: {original_size} records")

        before = len(df)
        df = df.dropna(subset=["clinical_npdr_grade"])
        logger.info(f"dropped null labels: {before - len(df)} removed, {len(df)} remaining")

        before = len(df)
        df = df.dropna(subset=["image_fundus_infrared_path"])
        logger.info(f"dropped null image paths: {before - len(df)} removed, {len(df)} remaining")

        before = len(df)
        df = df.drop_duplicates(subset=["image_fundus_infrared_path"], keep="first")
        logger.info(f"dropped duplicate image paths: {before - len(df)} removed, {len(df)} remaining")

        valid_grades = list(self.schema.ml_dataset.label_mapping.keys())
        before = len(df)
        df = df[df["clinical_npdr_grade"].isin(valid_grades)]
        logger.info(f"dropped invalid grades: {before - len(df)} removed, {len(df)} remaining")

        cleaned_csv = self.config.root_dir / "cleaned.csv"
        cleaned_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cleaned_csv, index=False)

        logger.info(f"clinical cleaning complete: {original_size} → {len(df)} records")
        logger.info(f"final grade distribution: {df['clinical_npdr_grade'].value_counts().to_dict()}")
        logger.info(f"cleaned CSV saved: {cleaned_csv}")
        return df