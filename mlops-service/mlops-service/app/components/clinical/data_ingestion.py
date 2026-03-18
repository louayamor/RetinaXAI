from collections import Counter
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from loguru import logger

from app.entity.config_entity import DataIngestionConfig


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_huggingface_dataset(self) -> None:
        cfg = self.config.huggingface
        save_path = cfg.root_dir / "huggingface" / "train"

        if save_path.exists() and any(save_path.iterdir()):
            logger.info(f"huggingface dataset already exists locally, skipping download: {save_path}")
            return

        logger.info(f"connecting to huggingface hub: {cfg.dataset_name}")
        split_str = f"{cfg.train_split}[:{cfg.max_samples}]" if cfg.max_samples else cfg.train_split
        logger.info(f"downloading split: {split_str}")

        ds = load_dataset(
            cfg.dataset_name,
            split=split_str,
        )

        logger.info(f"downloaded: {len(ds)} samples")
        logger.info(f"features: {list(ds.features.keys())}")

        from collections import Counter
        label_dist = dict(sorted(Counter(ds["label_code"]).items()))
        logger.info(f"label distribution: {label_dist}")

        logger.info(f"saving to disk: {save_path}")
        ds.save_to_disk(str(save_path))
        logger.info(f"dataset saved: {len(ds)} samples")
        
    def load_samaya_data(self) -> dict:
        cfg = self.config.samaya

        logger.info(f"loading samaya reports CSV: {cfg.reports_csv}")

        if not cfg.reports_csv.exists():
            logger.warning(f"samaya reports CSV not found: {cfg.reports_csv}")
            return {"images": [], "records": 0}

        df = pd.read_csv(cfg.reports_csv)
        logger.info(f"samaya CSV loaded: {len(df)} records, {len(df.columns)} columns")

        if "clinical_npdr_grade" in df.columns:
            grade_dist = df["clinical_npdr_grade"].value_counts().to_dict()
            logger.info(f"samaya grade distribution: {grade_dist}")

        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0].to_dict()
        if null_cols:
            logger.warning(f"samaya null values per column: {null_cols}")

        logger.info(f"scanning samaya fundus images: {cfg.images_dir}")
        valid_images = []
        missing = 0
        total = df["image_fundus_infrared_path"].dropna().shape[0]

        for i, path_str in enumerate(df["image_fundus_infrared_path"].dropna(), 1):
            p = Path(path_str)
            if p.exists():
                valid_images.append(str(p))
            else:
                missing += 1
            if i % 10 == 0 or i == total:
                logger.info(f"image scan progress: {i}/{total} checked, {len(valid_images)} valid, {missing} missing")

        if missing:
            logger.warning(f"samaya: {missing} fundus image paths not found on disk")

        logger.info(f"samaya ingestion complete: {len(valid_images)} valid images out of {total}")

        return {
            "records": len(df),
            "valid_images": len(valid_images),
            "missing_images": missing,
            "images": valid_images,
            "columns": list(df.columns),
        }

    def run(self) -> dict:
        logger.info("=" * 60)
        logger.info("data ingestion started")
        logger.info("=" * 60)

        logger.info("--- stage 1/2: huggingface dataset ---")
        self.download_huggingface_dataset()

        logger.info("--- stage 2/2: samaya hospital data ---")
        samaya_summary = self.load_samaya_data()

        summary = {
            "huggingface": {
                "train": str(self.config.huggingface.root_dir / "huggingface" / "train"),
            },
            "samaya": samaya_summary,
        }

        logger.info("=" * 60)
        logger.info("data ingestion complete")
        logger.info(f"huggingface saved: {summary['huggingface']['train']}")
        logger.info(f"samaya records: {samaya_summary['records']}")
        logger.info(f"samaya valid images: {samaya_summary['valid_images']}")
        logger.info(f"samaya missing images: {samaya_summary['missing_images']}")
        logger.info("=" * 60)

        return summary