import pickle
import mlflow
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    classification_report,
    roc_auc_score,
)
from xgboost import XGBClassifier

from app.entity.config_entity import ClinicalModelEvaluationConfig
from app.utils.common import load_json, read_yaml, save_json
from app.constants import PARAMS_FILE_PATH, SCHEMA_FILE_PATH
from monitoring.prometheus_metrics import QUADRATIC_WEIGHTED_KAPPA


class ClinicalModelEvaluation:
    def __init__(self, config: ClinicalModelEvaluationConfig):
        self.config = config
        self.params = read_yaml(PARAMS_FILE_PATH)
        self.schema = read_yaml(SCHEMA_FILE_PATH)

    def _load_model(self) -> tuple[XGBClassifier, int, list]:
        with open(self.config.model_path, "rb") as f:
            model = pickle.load(f)

        meta = load_json(self.config.model_path.parent / "feature_importance.json")
        label_offset = int(meta.get("label_offset", 0))
        feature_cols = list(meta.get("feature_cols", []))

        logger.info(f"model loaded from: {self.config.model_path}")
        logger.info(f"label offset: {label_offset}")
        logger.info(f"features: {feature_cols}")
        return model, label_offset, feature_cols

    def _load_data(self, feature_cols: list, label_offset: int) -> tuple:
        df = pd.read_csv(self.config.test_csv)
        df["label"] = df["label"] - label_offset

        available = [f for f in feature_cols if f in df.columns]
        missing = set(feature_cols) - set(available)
        if missing:
            logger.warning(f"missing features in test CSV: {missing}")

        X = df[available].values
        y = df["label"].values
        return X, y, available

    def _compute_auc(self, y: np.ndarray, probs: np.ndarray) -> float | None:
        present_classes = sorted(set(y))
        if len(present_classes) < 2:
            logger.warning("less than 2 classes present, skipping AUC")
            return None
        try:
            num_classes = len(np.unique(y))
            if num_classes == probs.shape[1]:
                return roc_auc_score(y, probs, multi_class="ovr", average="macro")
            else:
                probs_subset = probs[:, present_classes]
                probs_subset = probs_subset / probs_subset.sum(axis=1, keepdims=True)
                return roc_auc_score(
                    y,
                    probs_subset,
                    multi_class="ovr",
                    average="macro",
                    labels=present_classes,
                )
        except Exception as e:
            logger.warning(f"AUC computation failed: {e}")
            return None

    def evaluate(self) -> dict:
        logger.info("=" * 60)
        logger.info("clinical model evaluation started")
        logger.info("=" * 60)

        model, label_offset, feature_cols = self._load_model()
        X_test, y_test, available_features = self._load_data(feature_cols, label_offset)

        probs = model.predict_proba(X_test)
        preds = model.predict(X_test)

        accuracy = accuracy_score(y_test, preds)
        qwk = cohen_kappa_score(y_test, preds, weights="quadratic")
        auc = self._compute_auc(y_test, probs)
        report = classification_report(y_test, preds, output_dict=True, zero_division=0)

        auc_str = f"{auc:.4f}" if auc is not None else "N/A"
        logger.info(f"accuracy={accuracy:.4f} qwk={qwk:.4f} auc={auc_str}")
        logger.info(f"label distribution: {dict(zip(*np.unique(y_test, return_counts=True)))}")

        metrics = {
            "accuracy": round(accuracy, 4),
            "quadratic_weighted_kappa": round(qwk, 4),
            "roc_auc_macro": round(auc, 4) if auc is not None else None,
            "classification_report": report,
            "num_samples": len(y_test),
            "label_offset": label_offset,
            "features_used": available_features,
            "label_distribution": {
                str(int(k) + label_offset): int(v)
                for k, v in zip(*np.unique(y_test, return_counts=True))
            },
        }

        QUADRATIC_WEIGHTED_KAPPA.labels(
            pipeline="clinical", split="test"
        ).set(metrics["quadratic_weighted_kappa"])

        save_json(self.config.metric_file, metrics)
        logger.info(f"metrics saved: {self.config.metric_file}")

        with mlflow.start_run(run_name=self.config.run_name + "_eval"):
            mlflow.log_metrics({
                "test_accuracy": metrics["accuracy"],
                "test_qwk": metrics["quadratic_weighted_kappa"],
                "test_auc": metrics["roc_auc_macro"] or 0.0,
            })
            mlflow.log_artifact(str(self.config.metric_file))

        logger.info("=" * 60)
        logger.info("clinical model evaluation complete")
        logger.info(f"accuracy={accuracy:.4f} qwk={qwk:.4f} auc={auc_str}")
        logger.info("=" * 60)

        return metrics