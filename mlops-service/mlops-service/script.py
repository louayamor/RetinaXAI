# This script writes all content to individual files
import os

files = {}

files["imaging_components_init"] = ("app/components/imaging/__init__.py", "")
files["clinical_components_init"] = ("app/components/clinical/__init__.py", "")

files["imaging_data_ingestion"] = ("app/components/imaging/data_ingestion.py", '''from collections import Counter
from pathlib import Path

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
''')

files["imaging_data_cleaning"] = ("app/components/imaging/data_cleaning.py", '''from datasets import load_from_disk, Dataset
from loguru import logger

from app.entity.config_entity import ImagingCleaningConfig


class ImagingDataCleaning:
    def __init__(self, config: ImagingCleaningConfig):
        self.config = config

    def run(self) -> Dataset:
        source_path = self.config.source_dir / "huggingface" / "train"
        logger.info(f"loading dataset from: {source_path}")

        ds = load_from_disk(str(source_path))
        original_size = len(ds)
        logger.info(f"loaded: {original_size} samples")

        before = len(ds)
        ds = ds.filter(lambda x: x["label_code"] is not None)
        logger.info(f"dropped null labels: {before - len(ds)} removed, {len(ds)} remaining")

        before = len(ds)
        ds = ds.filter(lambda x: x["image"] is not None)
        logger.info(f"dropped null images: {before - len(ds)} removed, {len(ds)} remaining")

        clean_path = self.config.root_dir / "huggingface" / "train_clean"
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        ds.save_to_disk(str(clean_path))

        logger.info(f"imaging cleaning complete: {original_size} -> {len(ds)} samples")
        logger.info(f"clean dataset saved: {clean_path}")
        return ds
''')

files["imaging_data_transformation"] = ("app/components/imaging/data_transformation.py", '''import io
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
        logger.info(f"samaya label distribution: {df[\'label\'].value_counts().sort_index().to_dict()}")

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
        logger.info("imaging data transformation started")
        self._transform_eyepacs()
        self._transform_samaya()
        logger.info("imaging data transformation complete")
''')

files["imaging_model_trainer"] = ("app/components/imaging/model_trainer.py", '''class ImagingModelTrainer:
    pass
''')

files["imaging_model_evaluation"] = ("app/components/imaging/model_evaluation.py", '''class ImagingModelEvaluation:
    pass
''')

files["clinical_data_ingestion"] = ("app/components/clinical/data_ingestion.py", '''from pathlib import Path

import pandas as pd
from loguru import logger

from app.entity.config_entity import ClinicalIngestionConfig


class ClinicalDataIngestion:
    def __init__(self, config: ClinicalIngestionConfig):
        self.config = config

    def run(self) -> pd.DataFrame:
        logger.info(f"loading samaya reports CSV: {self.config.reports_csv}")

        if not self.config.reports_csv.exists():
            raise FileNotFoundError(f"samaya reports CSV not found: {self.config.reports_csv}")

        df = pd.read_csv(self.config.reports_csv)
        logger.info(f"loaded: {len(df)} records, {len(df.columns)} columns")

        if "clinical_npdr_grade" in df.columns:
            grade_dist = df["clinical_npdr_grade"].value_counts().to_dict()
            logger.info(f"grade distribution (raw): {grade_dist}")

        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0].to_dict()
        if null_cols:
            logger.warning(f"null values per column: {null_cols}")

        return df
''')

files["clinical_data_cleaning"] = ("app/components/clinical/data_cleaning.py", '''import pandas as pd
from loguru import logger

from app.entity.config_entity import ClinicalCleaningConfig
from app.utils.common import read_yaml
from app.constants import SCHEMA_FILE_PATH


class ClinicalDataCleaning:
    def __init__(self, config: ClinicalCleaningConfig):
        self.config = config
        self.schema = read_yaml(SCHEMA_FILE_PATH)

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
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

        logger.info(f"clinical cleaning complete: {original_size} -> {len(df)} records")
        logger.info(f"final grade distribution: {df[\'clinical_npdr_grade\'].value_counts().to_dict()}")
        return df
''')

files["clinical_data_transformation"] = ("app/components/clinical/data_transformation.py", '''import pandas as pd
from loguru import logger
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from app.entity.config_entity import ClinicalTransformationConfig
from app.utils.common import read_yaml, save_json
from app.constants import PARAMS_FILE_PATH, SCHEMA_FILE_PATH


class ClinicalDataTransformation:
    def __init__(self, config: ClinicalTransformationConfig):
        self.config = config
        self.params = read_yaml(PARAMS_FILE_PATH)
        self.schema = read_yaml(SCHEMA_FILE_PATH)

    def run(self, df: pd.DataFrame) -> None:
        logger.info("clinical data transformation started")

        label_mapping = dict(self.schema.ml_dataset.label_mapping)
        df["label"] = df["clinical_npdr_grade"].map(label_mapping).astype(int)
        logger.info(f"label encoding applied: {label_mapping}")

        numeric_features = list(self.params.ml_training.features.numeric)
        categorical_features = list(self.params.ml_training.features.categorical)
        all_features = numeric_features + categorical_features

        available_features = [f for f in all_features if f in df.columns]
        missing_features = set(all_features) - set(available_features)
        if missing_features:
            logger.warning(f"features not in CSV, will be dropped: {missing_features}")

        for col in categorical_features:
            if col in df.columns:
                df[col] = df[col].fillna("unknown")
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))

        for col in numeric_features:
            if col in df.columns:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                logger.info(f"imputed {col} with median: {median_val:.4f}")

        feature_cols = [f for f in available_features if f in df.columns]
        df_features = df[feature_cols + ["label"]]

        train_df, test_df = train_test_split(
            df_features,
            test_size=self.params.ml_training.test_size,
            random_state=self.params.ml_training.seed,
            stratify=df_features["label"],
        )

        self.config.train_csv.parent.mkdir(parents=True, exist_ok=True)
        train_df.to_csv(self.config.train_csv, index=False)
        test_df.to_csv(self.config.test_csv, index=False)

        logger.info(f"clinical train CSV saved: {self.config.train_csv} ({len(train_df)} rows)")
        logger.info(f"clinical test CSV saved: {self.config.test_csv} ({len(test_df)} rows)")

        feature_meta = {
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "available_features": feature_cols,
            "missing_features": list(missing_features),
            "train_samples": len(train_df),
            "test_samples": len(test_df),
        }
        save_json(self.config.feature_file, feature_meta)
        logger.info(f"feature metadata saved: {self.config.feature_file}")
        logger.info("clinical data transformation complete")
''')

files["clinical_model_trainer"] = ("app/components/clinical/model_trainer.py", '''class ClinicalModelTrainer:
    pass
''')

files["clinical_model_evaluation"] = ("app/components/clinical/model_evaluation.py", '''class ClinicalModelEvaluation:
    pass
''')

files["imaging_pipeline_init"] = ("app/pipeline/imaging/__init__.py", "")
files["clinical_pipeline_init"] = ("app/pipeline/clinical/__init__.py", "")

files["imaging_stage_01"] = ("app/pipeline/imaging/stage_01_data_ingestion.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.data_ingestion import ImagingDataIngestion


def run():
    logger.info(">>> stage 01: imaging data ingestion started")
    manager = ConfigurationManager()
    ImagingDataIngestion(manager.get_imaging_ingestion_config()).run()
    logger.info(">>> stage 01: imaging data ingestion complete")


if __name__ == "__main__":
    run()
''')

files["imaging_stage_02"] = ("app/pipeline/imaging/stage_02_data_cleaning.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.data_cleaning import ImagingDataCleaning


def run():
    logger.info(">>> stage 02: imaging data cleaning started")
    manager = ConfigurationManager()
    ImagingDataCleaning(manager.get_imaging_cleaning_config()).run()
    logger.info(">>> stage 02: imaging data cleaning complete")


if __name__ == "__main__":
    run()
''')

files["imaging_stage_03"] = ("app/pipeline/imaging/stage_03_data_transformation.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.data_transformation import ImagingDataTransformation


def run():
    logger.info(">>> stage 03: imaging data transformation started")
    manager = ConfigurationManager()
    ImagingDataTransformation(manager.get_imaging_transformation_config()).run()
    logger.info(">>> stage 03: imaging data transformation complete")


if __name__ == "__main__":
    run()
''')

files["imaging_stage_04"] = ("app/pipeline/imaging/stage_04_model_trainer.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.model_trainer import ImagingModelTrainer


def run():
    logger.info(">>> stage 04: imaging model training started")
    manager = ConfigurationManager()
    cfg = manager.get_imaging_model_trainer_config()
    transformation_cfg = manager.get_imaging_transformation_config()
    ImagingModelTrainer(cfg, transformation_cfg).train()
    logger.info(">>> stage 04: imaging model training complete")


if __name__ == "__main__":
    run()
''')

files["imaging_stage_05"] = ("app/pipeline/imaging/stage_05_model_evaluation.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.model_evaluation import ImagingModelEvaluation


def run():
    logger.info(">>> stage 05: imaging model evaluation started")
    manager = ConfigurationManager()
    ImagingModelEvaluation(manager.get_imaging_model_evaluation_config()).evaluate()
    logger.info(">>> stage 05: imaging model evaluation complete")


if __name__ == "__main__":
    run()
''')

files["clinical_stage_01"] = ("app/pipeline/clinical/stage_01_data_ingestion.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.data_ingestion import ClinicalDataIngestion


def run():
    logger.info(">>> stage 01: clinical data ingestion started")
    manager = ConfigurationManager()
    ClinicalDataIngestion(manager.get_clinical_ingestion_config()).run()
    logger.info(">>> stage 01: clinical data ingestion complete")


if __name__ == "__main__":
    run()
''')

files["clinical_stage_02"] = ("app/pipeline/clinical/stage_02_data_cleaning.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.data_ingestion import ClinicalDataIngestion
from app.components.clinical.data_cleaning import ClinicalDataCleaning


def run():
    logger.info(">>> stage 02: clinical data cleaning started")
    manager = ConfigurationManager()
    df = ClinicalDataIngestion(manager.get_clinical_ingestion_config()).run()
    ClinicalDataCleaning(manager.get_clinical_cleaning_config()).run(df)
    logger.info(">>> stage 02: clinical data cleaning complete")


if __name__ == "__main__":
    run()
''')

files["clinical_stage_03"] = ("app/pipeline/clinical/stage_03_data_transformation.py", '''from loguru import logger
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
''')

files["clinical_stage_04"] = ("app/pipeline/clinical/stage_04_model_trainer.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.model_trainer import ClinicalModelTrainer


def run():
    logger.info(">>> stage 04: clinical model training started")
    manager = ConfigurationManager()
    cfg = manager.get_clinical_model_trainer_config()
    transformation_cfg = manager.get_clinical_transformation_config()
    ClinicalModelTrainer(cfg, transformation_cfg).train()
    logger.info(">>> stage 04: clinical model training complete")


if __name__ == "__main__":
    run()
''')

files["clinical_stage_05"] = ("app/pipeline/clinical/stage_05_model_evaluation.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.clinical.model_evaluation import ClinicalModelEvaluation


def run():
    logger.info(">>> stage 05: clinical model evaluation started")
    manager = ConfigurationManager()
    ClinicalModelEvaluation(manager.get_clinical_model_evaluation_config()).evaluate()
    logger.info(">>> stage 05: clinical model evaluation complete")


if __name__ == "__main__":
    run()
''')

files["training_pipeline"] = ("app/pipeline/training_pipeline.py", '''from loguru import logger
from app.config.configuration import ConfigurationManager
from app.pipeline.imaging.stage_01_data_ingestion import run as imaging_ingest
from app.pipeline.imaging.stage_02_data_cleaning import run as imaging_clean
from app.pipeline.imaging.stage_03_data_transformation import run as imaging_transform
from app.pipeline.imaging.stage_04_model_trainer import run as imaging_train
from app.pipeline.imaging.stage_05_model_evaluation import run as imaging_evaluate
from app.pipeline.clinical.stage_01_data_ingestion import run as clinical_ingest
from app.pipeline.clinical.stage_02_data_cleaning import run as clinical_clean
from app.pipeline.clinical.stage_03_data_transformation import run as clinical_transform
from app.pipeline.clinical.stage_04_model_trainer import run as clinical_train
from app.pipeline.clinical.stage_05_model_evaluation import run as clinical_evaluate


class TrainingPipeline:
    def run_imaging(self):
        logger.info("=== imaging pipeline started ===")
        imaging_ingest()
        imaging_clean()
        imaging_transform()
        imaging_train()
        imaging_evaluate()
        logger.info("=== imaging pipeline complete ===")

    def run_clinical(self):
        logger.info("=== clinical pipeline started ===")
        clinical_ingest()
        clinical_clean()
        clinical_transform()
        clinical_train()
        clinical_evaluate()
        logger.info("=== clinical pipeline complete ===")

    def run(self):
        logger.info("=== unified training pipeline started ===")
        self.run_imaging()
        self.run_clinical()
        logger.info("=== unified training pipeline complete ===")
''')

files["inference_pipeline"] = ("app/pipeline/inference_pipeline.py", '''class InferencePipeline:
    pass
''')

for key, (path, content) in files.items():
    with open(path, "w") as f:
        f.write(content)
    print(f"written: {path}")

print("\nall files written successfully")