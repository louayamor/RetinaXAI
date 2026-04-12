from collections import Counter
import shutil
import tempfile

from datasets import concatenate_datasets, load_dataset, load_from_disk
from loguru import logger

from app.entity.config_entity import ImagingIngestionConfig


class ImagingDataIngestion:
    def __init__(self, config: ImagingIngestionConfig):
        self.config = config

    def run(self) -> None:
        save_path = self.config.root_dir / "huggingface" / "train"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"starting imaging ingestion: save_path={save_path}")

        existing_ds = None
        existing_size = 0
        if save_path.exists() and any(save_path.iterdir()):
            try:
                existing_ds = load_from_disk(str(save_path))
                existing_size = len(existing_ds)
                logger.info(
                    f"loaded existing huggingface dataset: {save_path} ({existing_size} samples)"
                )
            except Exception as e:
                logger.warning(
                    f"failed to load existing dataset at {save_path}, rebuilding from source: {e}"
                )

        target_size = self.config.max_samples
        if target_size is not None and existing_size >= target_size:
            logger.info(
                f"existing dataset already satisfies max_samples={target_size}, skipping download"
            )
            return

        start_idx = existing_size if existing_ds is not None else 0
        split_str = self.config.train_split
        if target_size is not None:
            split_str = f"{self.config.train_split}[{start_idx}:{target_size}]"
        elif start_idx:
            split_str = f"{self.config.train_split}[{start_idx}:]"

        if existing_ds is not None:
            logger.info(
                f"incremental ingestion enabled: existing={existing_size}, target={target_size}, requesting={split_str}"
            )
        else:
            logger.info(
                f"fresh ingestion run: requesting={split_str}, target={target_size}"
            )

        logger.info(f"connecting to huggingface hub: {self.config.dataset_name}")
        logger.info(f"downloading split: {split_str}")

        ds = load_dataset(self.config.dataset_name, split=split_str)

        downloaded_size = len(ds)
        logger.info(f"downloaded {downloaded_size} new samples from huggingface")

        if existing_ds is not None:
            if len(ds) == 0:
                logger.info(
                    f"no new samples available; keeping existing dataset with {existing_size} samples"
                )
                return
            ds = concatenate_datasets([existing_ds, ds])
            logger.info(
                f"merged dataset: existing={existing_size}, new={downloaded_size}, total={len(ds)}"
            )

        logger.info(f"downloaded: {len(ds)} samples")
        logger.info(f"features: {list(ds.features.keys())}")
        logger.info(
            f"label distribution: {dict(sorted(Counter(ds['label_code']).items()))}"
        )

        logger.info(f"saving to disk: {save_path}")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = tmp_dir + "/dataset"
            ds.save_to_disk(tmp_path)
            if save_path.exists():
                shutil.rmtree(save_path)
            shutil.move(tmp_path, save_path)

        logger.info(f"dataset saved: {len(ds)} samples")
