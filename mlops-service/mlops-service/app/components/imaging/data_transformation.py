import io
from pathlib import Path

import pandas as pd
from datasets import load_from_disk
from loguru import logger
from PIL import Image
from sklearn.model_selection import train_test_split

from app.entity.config_entity import ImagingTransformationConfig
from app.utils.common import read_yaml
from app.constants import PARAMS_FILE_PATH, SCHEMA_FILE_PATH


class ImagingDataTransformation:
    def __init__(self, config: ImagingTransformationConfig):
        self.config = config
        self.params = read_yaml(PARAMS_FILE_PATH)
        self.schema = read_yaml(SCHEMA_FILE_PATH)

    def _resize_and_save(self, img: Image.Image, path: Path) -> None:
        img.convert("RGB").resize(
            (self.config.image_size, self.config.image_size)
        ).save(path)

    def _transform_eyepacs(self) -> None:
        source_path = self.config.source_dir / "huggingface" / "train_clean"
        logger.info(f"loading clean eyepacs dataset: {source_path}")
        ds = load_from_disk(str(source_path))

        split_cfg = self.schema.dl_dataset.train_test_split
        indices = list(range(len(ds)))
        train_idx, test_idx = train_test_split(
            indices,
            test_size=split_cfg.test_size,
            random_state=split_cfg.seed,
            stratify=ds["label_code"],
        )
        logger.info(f"stratified split: {len(train_idx)} train, {len(test_idx)} test")

        for split_name, split_indices, csv_path in [
            ("train", train_idx, self.config.train_csv),
            ("test", test_idx, self.config.test_csv),
        ]:
            output_dir = self.config.root_dir / "images" / "eyepacs" / split_name
            output_dir.mkdir(parents=True, exist_ok=True)
            records = []
            total = len(split_indices)

            for i, idx in enumerate(split_indices, 1):
                sample = ds[idx]
                img = sample["image"]
                if not isinstance(img, Image.Image):
                    img = Image.open(io.BytesIO(img["bytes"]))
                img_path = output_dir / f"{idx}.png"
                self._resize_and_save(img, img_path)
                records.append({
                    "image_path": str(img_path),
                    "label": sample["label_code"],
                    "source": "eyepacs",
                })
                if i % 500 == 0 or i == total:
                    logger.info(f"eyepacs {split_name}: {i}/{total} processed")

            pd.DataFrame(records).to_csv(csv_path, index=False)
            logger.info(f"eyepacs {split_name} CSV saved: {csv_path} ({len(records)} rows)")

    def _transform_samaya(self) -> None:
        label_mapping = dict(self.schema.ml_dataset.label_mapping)
        source_csv = Path("artifacts/ocr/output/reports.csv")

        if not source_csv.exists():
            logger.warning(f"samaya reports CSV not found: {source_csv}")
            return

        df = pd.read_csv(source_csv)
        df = df.dropna(subset=["clinical_npdr_grade", "image_fundus_infrared_path"])
        df = df.drop_duplicates(subset=["image_fundus_infrared_path"], keep="first")
        df["label"] = df["clinical_npdr_grade"].map(label_mapping)
        df = df.dropna(subset=["label"])
        df["label"] = df["label"].astype(int)

        logger.info(f"samaya usable samples: {len(df)}")
        logger.info(f"samaya label distribution: {df['label'].value_counts().sort_index().to_dict()}")

        output_dir = self.config.root_dir / "images" / "samaya"
        output_dir.mkdir(parents=True, exist_ok=True)

        records = []
        skipped = 0
        total = len(df)

        for i, (_, row) in enumerate(df.iterrows(), 1):
            src_path = Path(row["image_fundus_infrared_path"])
            if not src_path.exists():
                skipped += 1
                continue
            img_path = output_dir / f"{i}.png"
            self._resize_and_save(Image.open(src_path), img_path)
            records.append({
                "image_path": str(img_path),
                "label": row["label"],
                "source": "samaya",
            })
            if i % 10 == 0 or i == total:
                logger.info(f"samaya: {i}/{total} processed")

        if skipped:
            logger.warning(f"samaya: skipped {skipped} images not found on disk")

        pd.DataFrame(records).to_csv(self.config.samaya_csv, index=False)
        logger.info(f"samaya CSV saved: {self.config.samaya_csv} ({len(records)} rows)")

    def run(self) -> None:
        if self.config.train_csv.exists() and self.config.test_csv.exists():
            logger.info("transformation outputs already exist, skipping")
            return
        logger.info("imaging data transformation started")
        self._transform_eyepacs()
        self._transform_samaya()
        logger.info("imaging data transformation complete")
