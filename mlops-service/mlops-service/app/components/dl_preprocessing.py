import io

import pandas as pd
from datasets import load_from_disk
from loguru import logger
from pathlib import Path
from PIL import Image

from app.entity.config_entity import DLPreprocessingConfig


class DLPreprocessing:
    def __init__(self, config: DLPreprocessingConfig):
        self.config = config

    def _resize_and_save(self, img: Image.Image, path: Path) -> None:
        img.convert("RGB").resize(
            (self.config.image_size, self.config.image_size)
        ).save(path)

    def _process_huggingface_split(self, split: str, csv_path: Path) -> None:
        ds = load_from_disk(str(self.config.source_dir / "huggingface" / split))
        output_dir = self.config.root_dir / "images" / "huggingface" / split
        output_dir.mkdir(parents=True, exist_ok=True)

        records = []
        for idx, sample in enumerate(ds):
            img = sample["image"]
            if not isinstance(img, Image.Image):
                img = Image.open(io.BytesIO(img["bytes"]))
            img_path = output_dir / f"{idx}.png"
            self._resize_and_save(img, img_path)
            records.append({
                "image_path": str(img_path),
                "label": sample["label"],
                "source": "huggingface",
            })

        pd.DataFrame(records).to_csv(csv_path, index=False)
        logger.info(f"huggingface {split} CSV saved: {csv_path} ({len(records)} rows)")

    def _process_samaya_images(self) -> None:
        reports_csv = self.config.source_dir.parent.parent / "ocr" / "output" / "reports.csv"

        if not reports_csv.exists():
            logger.warning(f"samaya reports CSV not found: {reports_csv}")
            return

        df = pd.read_csv(reports_csv)

        required = {"clinical_npdr_grade", "image_fundus_infrared_path"}
        if not required.issubset(df.columns):
            logger.warning(f"samaya CSV missing required columns: {required - set(df.columns)}")
            return

        df = df.dropna(subset=["clinical_npdr_grade", "image_fundus_infrared_path"])

        output_dir = self.config.root_dir / "images" / "samaya"
        output_dir.mkdir(parents=True, exist_ok=True)

        records = []
        skipped = 0
        for idx, row in df.iterrows():
            src_path = Path(row["image_fundus_infrared_path"])
            if not src_path.exists():
                skipped += 1
                continue
            img_path = output_dir / f"{idx}.png"
            self._resize_and_save(Image.open(src_path), img_path)
            records.append({
                "image_path": str(img_path),
                "label": int(row["clinical_npdr_grade"]),
                "source": "samaya",
            })

        if skipped:
            logger.warning(f"samaya: skipped {skipped} images not found on disk")

        pd.DataFrame(records).to_csv(self.config.samaya_csv, index=False)
        logger.info(f"samaya CSV saved: {self.config.samaya_csv} ({len(records)} rows)")

    def run(self) -> None:
        logger.info("DL preprocessing started")

        self._process_huggingface_split("train", self.config.train_csv)
        self._process_huggingface_split("test", self.config.test_csv)
        self._process_samaya_images()

        logger.info("DL preprocessing complete")