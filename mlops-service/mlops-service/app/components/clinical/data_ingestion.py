from pathlib import Path

import pandas as pd
from loguru import logger

from app.entity.config_entity import ClinicalIngestionConfig


class ClinicalDataIngestion:
    def __init__(self, config: ClinicalIngestionConfig):
        self.config = config

    def run(self) -> pd.DataFrame:
        raw_csv = self.config.raw_csv

        if raw_csv.exists():
            logger.info(f"raw CSV already exists, skipping ingestion: {raw_csv}")
            return pd.read_csv(raw_csv)

        logger.info(f"loading samaya reports CSV: {self.config.reports_csv}")

        if not self.config.reports_csv.exists():
            raise FileNotFoundError(f"samaya reports CSV not found: {self.config.reports_csv}")

        df = pd.read_csv(self.config.reports_csv)
        logger.info(f"loaded: {len(df)} records, {len(df.columns)} columns")

        if "clinical_npdr_grade" in df.columns:
            logger.info(f"grade distribution (raw): {df['clinical_npdr_grade'].value_counts().to_dict()}")

        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0].to_dict()
        if null_cols:
            logger.warning(f"null values per column: {null_cols}")

        raw_csv = self.config.raw_csv
        raw_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_csv, index=False)
        logger.info(f"raw CSV saved: {raw_csv} ({len(df)} rows)")

        return df