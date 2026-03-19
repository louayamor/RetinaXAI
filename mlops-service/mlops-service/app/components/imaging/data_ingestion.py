from collections import Counter
from datasets import load_dataset
from loguru import logger

from app.entity.config_entity import ImagingIngestionConfig


class ImagingDataIngestion:
    def __init__(self, config: ImagingIngestionConfig):
        self.config = config

    def run(self) -> None:
        save_path = self.config.root_dir / "huggingface" / "train"

        if save_path.exists() and any(save_path.iterdir()):
            logger.info(f"huggingface dataset already exists, skipping download: {save_path}")
            return

        logger.info(f"connecting to huggingface hub: {self.config.dataset_name}")
        split_str = (
            f"{self.config.train_split}[:{self.config.max_samples}]"
            if self.config.max_samples
            else self.config.train_split
        )
        logger.info(f"downloading split: {split_str}")

        ds = load_dataset(self.config.dataset_name, split=split_str)

        logger.info(f"downloaded: {len(ds)} samples")
        logger.info(f"features: {list(ds.features.keys())}")
        logger.info(f"label distribution: {dict(sorted(Counter(ds['label_code']).items()))}")

        logger.info(f"saving to disk: {save_path}")
        ds.save_to_disk(str(save_path))
        logger.info(f"dataset saved: {len(ds)} samples")
