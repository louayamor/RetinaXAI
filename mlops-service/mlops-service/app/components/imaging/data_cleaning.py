from datasets import load_from_disk, Dataset
from loguru import logger

from app.entity.config_entity import ImagingCleaningConfig


class ImagingDataCleaning:
    def __init__(self, config: ImagingCleaningConfig):
        self.config = config

    def run(self) -> Dataset:  # type: ignore[type-var]
        clean_path = self.config.root_dir / "huggingface" / "train_clean"

        if clean_path.exists() and any(clean_path.iterdir()):
            logger.info(f"clean dataset already exists, skipping cleaning: {clean_path}")
            return load_from_disk(str(clean_path))  # type: ignore[return-value]
        
        source_path = self.config.source_dir / "huggingface" / "train"
        logger.info(f"loading dataset from: {source_path}")

        ds = load_from_disk(str(source_path))  # type: ignore[return-value]
        original_size = len(ds)
        logger.info(f"loaded: {original_size} samples")

        before = len(ds)
        ds = ds.filter(lambda x: x["label_code"] is not None)  # type: ignore[return-value]
        logger.info(f"dropped null labels: {before - len(ds)} removed, {len(ds)} remaining")

        before = len(ds)
        ds = ds.filter(lambda x: x["image"] is not None)  # type: ignore[return-value]
        logger.info(f"dropped null images: {before - len(ds)} removed, {len(ds)} remaining")

        clean_path = self.config.root_dir / "huggingface" / "train_clean"
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        ds.save_to_disk(str(clean_path))

        logger.info(f"imaging cleaning complete: {original_size} -> {len(ds)} samples")
        logger.info(f"clean dataset saved: {clean_path}")
        return ds  # type: ignore[return-value]
