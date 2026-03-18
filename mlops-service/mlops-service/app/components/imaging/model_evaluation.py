import mlflow
import mlflow.pytorch
import timm
import torch
import torch.nn as nn
from loguru import logger
from pathlib import Path
from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    classification_report,
    roc_auc_score,
)
import numpy as np
import pandas as pd

from app.components.imaging.model_trainer import RetinalDataset
from app.entity.config_entity import ImagingModelEvaluationConfig
from app.utils.common import read_yaml, save_json
from app.constants import PARAMS_FILE_PATH, SCHEMA_FILE_PATH


class ImagingModelEvaluation:
    def __init__(self, config: ImagingModelEvaluationConfig):
        self.config = config
        self.params = read_yaml(PARAMS_FILE_PATH)
        self.schema = read_yaml(SCHEMA_FILE_PATH)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"evaluation device: {self.device}")

    def _load_model(self) -> nn.Module:
        p = self.params.dl_training
        model = timm.create_model(
            "efficientnet_b3",
            pretrained=False,
            num_classes=p.num_classes,
            drop_rate=p.dropout,
        )
        model.load_state_dict(
            torch.load(self.config.model_path, map_location=self.device)
        )
        model.to(self.device)
        model.eval()
        logger.info(f"model loaded from: {self.config.model_path}")
        return model

    def _build_transform(self):
        norm = self.params.augmentation.normalize
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=norm.mean, std=norm.std),
        ])

    def _run_inference(self, model: nn.Module, csv_path: Path) -> tuple:
        tf = self._build_transform()
        loader = DataLoader(
            RetinalDataset(csv_path, tf),
            batch_size=self.params.evaluation.dl.batch_size,
            shuffle=False,
            num_workers=self.params.evaluation.dl.num_workers,
            pin_memory=True,
        )

        all_preds, all_labels, all_probs = [], [], []
        total = len(loader)

        with torch.no_grad():
            for i, (images, labels) in enumerate(loader, 1):
                images = images.to(self.device)
                outputs = model(images)
                probs = torch.softmax(outputs, dim=1).cpu().numpy()
                preds = outputs.argmax(1).cpu().tolist()

                all_probs.extend(probs)
                all_preds.extend(preds)
                all_labels.extend(labels.tolist())

                if i % 10 == 0 or i == total:
                    logger.info(f"inference progress: {i}/{total} batches")

        return all_preds, all_labels, np.array(all_probs)

    def _compute_auc(self, labels: list, probs: np.ndarray) -> float | None:
        num_classes = self.params.dl_training.num_classes
        present_classes = sorted(set(labels))

        if len(present_classes) < 2:
            logger.warning("less than 2 classes present, skipping AUC")
            return None

        try:
            if len(present_classes) == num_classes:
                return roc_auc_score(
                    labels, probs, multi_class="ovr", average="macro"
                )
            else:
                probs_subset = probs[:, present_classes]
                probs_subset = probs_subset / probs_subset.sum(axis=1, keepdims=True)
                return roc_auc_score(
                    labels,
                    probs_subset,
                    multi_class="ovr",
                    average="macro",
                    labels=present_classes,
                )
        except Exception as e:
            logger.warning(f"AUC computation failed: {e}")
            return None

    def _compute_metrics(
        self,
        preds: list,
        labels: list,
        probs: np.ndarray,
        split_name: str,
    ) -> dict:
        accuracy = accuracy_score(labels, preds)
        qwk = cohen_kappa_score(labels, preds, weights="quadratic")
        report = classification_report(labels, preds, output_dict=True, zero_division=0)
        auc = self._compute_auc(labels, probs)

        auc_str = f"{auc:.4f}" if auc is not None else "N/A"
        logger.info(
            f"[{split_name}] accuracy={accuracy:.4f} qwk={qwk:.4f} auc={auc_str}"
        )

        return {
            "split": split_name,
            "accuracy": round(accuracy, 4),
            "quadratic_weighted_kappa": round(qwk, 4),
            "roc_auc_macro": round(auc, 4) if auc is not None else None,
            "classification_report": report,
            "num_samples": len(labels),
            "label_distribution": {
                str(k): int(v)
                for k, v in pd.Series(labels).value_counts().sort_index().items()
            },
        }

    def evaluate(self) -> dict:
        logger.info("=" * 60)
        logger.info("imaging model evaluation started")
        logger.info("=" * 60)

        model = self._load_model()

        logger.info("--- evaluating on EyePACS test set ---")
        test_preds, test_labels, test_probs = self._run_inference(
            model, self.config.test_csv
        )
        test_metrics = self._compute_metrics(
            test_preds, test_labels, test_probs, "eyepacs_test"
        )

        samaya_metrics = None
        if self.config.samaya_csv.exists():
            logger.info("--- evaluating on Samaya domain validation set ---")
            samaya_preds, samaya_labels, samaya_probs = self._run_inference(
                model, self.config.samaya_csv
            )
            samaya_metrics = self._compute_metrics(
                samaya_preds, samaya_labels, samaya_probs, "samaya_validation"
            )
        else:
            logger.warning(f"samaya CSV not found, skipping: {self.config.samaya_csv}")

        full_metrics = {
            "eyepacs_test": test_metrics,
            "samaya_validation": samaya_metrics,
        }

        save_json(self.config.metric_file, full_metrics)
        logger.info(f"metrics saved: {self.config.metric_file}")

        with mlflow.start_run(run_name=self.config.run_name + "_eval"):
            mlflow.log_metrics({
                "test_accuracy": test_metrics["accuracy"],
                "test_qwk": test_metrics["quadratic_weighted_kappa"],
                "test_auc": test_metrics["roc_auc_macro"] or 0.0,
            })
            if samaya_metrics:
                mlflow.log_metrics({
                    "samaya_accuracy": samaya_metrics["accuracy"],
                    "samaya_qwk": samaya_metrics["quadratic_weighted_kappa"],
                    "samaya_auc": samaya_metrics["roc_auc_macro"] or 0.0,
                })
            mlflow.log_artifact(str(self.config.metric_file))

        logger.info("=" * 60)
        logger.info("imaging model evaluation complete")
        logger.info(f"eyepacs test  → accuracy={test_metrics['accuracy']:.4f} qwk={test_metrics['quadratic_weighted_kappa']:.4f}")
        if samaya_metrics:
            logger.info(f"samaya domain → accuracy={samaya_metrics['accuracy']:.4f} qwk={samaya_metrics['quadratic_weighted_kappa']:.4f}")
        logger.info("=" * 60)

        return full_metrics