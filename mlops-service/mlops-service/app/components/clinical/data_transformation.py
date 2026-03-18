import pandas as pd
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

    def run(self) -> None:
        if self.config.train_csv.exists() and self.config.test_csv.exists():
            logger.info("transformation outputs already exist, skipping")
            return
        
        logger.info("clinical data transformation started")

        cleaned_csv = self.config.root_dir / "cleaned.csv"
        logger.info(f"loading cleaned CSV: {cleaned_csv}")
        df = pd.read_csv(cleaned_csv)
        df = df.copy()

        label_mapping = dict(self.schema.ml_dataset.label_mapping)
        df["label"] = df["clinical_npdr_grade"].map(label_mapping).astype(int)
        logger.info(f"label encoding applied: {label_mapping}")

        numeric_features = list(self.params.ml_training.features.numeric)
        categorical_features = list(self.params.ml_training.features.categorical)
        all_features = numeric_features + categorical_features

        available_features = [f for f in all_features if f in df.columns]
        missing_features = set(all_features) - set(available_features)
        if missing_features:
            logger.warning(f"features not in CSV, skipping: {missing_features}")

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

        logger.info(f"clinical train CSV: {self.config.train_csv} ({len(train_df)} rows)")
        logger.info(f"clinical test CSV: {self.config.test_csv} ({len(test_df)} rows)")

        save_json(self.config.feature_file, {
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "available_features": feature_cols,
            "missing_features": list(missing_features),
            "train_samples": len(train_df),
            "test_samples": len(test_df),
        })
        logger.info("clinical data transformation complete")