from pathlib import Path

from datasets import load_dataset
from loguru import logger
import pandas as pd

from app.entity.config_entity import DataIngestionConfig


class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_huggingface_dataset(self) -> None:
        cfg = self.config.huggingface
        logger.info(f"loading huggingface dataset: {cfg.dataset_name}")

        train_ds = load_dataset(
            cfg.dataset_name,
            split=cfg.train_split,
            trust_remote_code=True,
        )
        test_ds = load_dataset(
            cfg.dataset_name,
            split=cfg.test_split,
            trust_remote_code=True,
        )

        train_ds.save_to_disk(str(cfg.root_dir / "huggingface" / "train"))
        test_ds.save_to_disk(str(cfg.root_dir / "huggingface" / "test"))

        logger.info(f"huggingface train samples: {len(train_ds)}")
        logger.info(f"huggingface test samples: {len(test_ds)}")

    def load_samaya_data(self) -> dict:
        cfg = self.config.samaya

        if not cfg.reports_csv.exists():
            logger.warning(f"samaya reports CSV not found: {cfg.reports_csv}")
            return {"images": [], "records": 0}

        df = pd.read_csv(cfg.reports_csv)
        logger.info(f"samaya CSV loaded: {len(df)} records, {len(df.columns)} columns")

        if not cfg.images_dir.exists():
            logger.warning(f"samaya images directory not found: {cfg.images_dir}")
            return {"images": [], "records": len(df)}

        valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
        images = [
            p for p in cfg.images_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in valid_extensions
        ]
        logger.info(f"samaya images found: {len(images)}")

        return {
            "records": len(df),
            "images": [str(p) for p in images],
            "columns": list(df.columns),
        }

    def run(self) -> dict:
        logger.info("data ingestion started")

        self.download_huggingface_dataset()
        samaya_summary = self.load_samaya_data()

        summary = {
            "huggingface": {
                "train": str(self.config.huggingface.root_dir / "huggingface" / "train"),
                "test": str(self.config.huggingface.root_dir / "huggingface" / "test"),
            },
            "samaya": samaya_summary,
        }

        logger.info(f"data ingestion complete: {summary}")
        return summary