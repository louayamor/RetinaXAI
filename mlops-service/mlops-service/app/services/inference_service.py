import io
import pickle
import numpy as np
import pandas as pd
import timm
import torch
import torch.nn as nn
from loguru import logger
from pathlib import Path
from PIL import Image
from torchvision import transforms

from app.api.schemas import ClinicalFeatures
from app.config.settings import Settings
from app.utils.common import load_json, read_yaml
from app.constants import PARAMS_FILE_PATH, SCHEMA_FILE_PATH


DR_CLASSES = {0: "No DR", 1: "Mild", 2: "Moderate", 3: "Severe", 4: "Proliferative DR"}


class InferenceService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.params = read_yaml(PARAMS_FILE_PATH)
        self.schema = read_yaml(SCHEMA_FILE_PATH)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._imaging_model = None
        self._clinical_model = None
        self._feature_meta = None

    def _load_imaging_model(self) -> nn.Module:
        if self._imaging_model is not None:
            return self._imaging_model
        p = self.params.dl_training
        model = timm.create_model(
            "efficientnet_b3",
            pretrained=False,
            num_classes=p.num_classes,
            drop_rate=p.dropout,
        )
        model.load_state_dict(
            torch.load(self.settings.imaging_model_path, map_location=self.device)
        )
        model.to(self.device)
        model.eval()
        self._imaging_model = model
        logger.info("imaging model loaded for inference")
        return model

    def _load_clinical_model(self):
        if self._clinical_model is not None:
            return self._clinical_model, self._feature_meta
        with open(self.settings.clinical_model_path, "rb") as f:
            model = pickle.load(f)
        feature_meta = load_json(self.settings.clinical_feature_importance_path)
        self._clinical_model = model
        self._feature_meta = feature_meta
        logger.info("clinical model loaded for inference")
        return model, feature_meta

    def _build_transform(self):
        norm = self.params.augmentation.normalize
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=norm.mean, std=norm.std),
        ])

    def predict_imaging(self, image_bytes: bytes) -> dict:
        model = self._load_imaging_model()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tf = self._build_transform()
        tensor = tf(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = model(tensor)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]

        pred_class = int(np.argmax(probs))
        confidence = float(probs[pred_class])

        return {
            "predicted_grade": pred_class,
            "predicted_label": DR_CLASSES[pred_class],
            "confidence": round(confidence, 4),
            "probabilities": {
                DR_CLASSES[i]: round(float(p), 4)
                for i, p in enumerate(probs)
            },
        }

    def predict_clinical(self, features: ClinicalFeatures) -> dict:
        model, feature_meta = self._load_clinical_model()
        label_offset = feature_meta.get("label_offset", 0)
        feature_cols = feature_meta.get("feature_cols", [])

        label_mapping = dict(self.schema.ml_dataset.label_mapping)
        from sklearn.preprocessing import LabelEncoder

        feature_dict = features.model_dump()
        row = {}
        for col in feature_cols:
            val = feature_dict.get(col)
            if col in ["patient_gender", "meta_eye", "clinical_edema", "clinical_erm_status", "meta_image_quality"]:
                le = LabelEncoder()
                le.fit(["unknown", "M", "F", "OD", "OS", "present", "absent", "residual", "poor", "adequate", "good"])
                row[col] = le.transform([val if val is not None else "unknown"])[0]
            else:
                row[col] = val if val is not None else 0.0

        X = pd.DataFrame([row])[feature_cols].values
        pred_0indexed = int(model.predict(X)[0])
        pred_original = pred_0indexed + label_offset
        probs = model.predict_proba(X)[0]

        risk_labels = {1: "Mild NPDR", 2: "Moderate NPDR", 3: "Severe NPDR"}

        return {
            "predicted_grade": pred_original,
            "predicted_label": risk_labels.get(pred_original, "Unknown"),
            "risk_score": round(float(max(probs)), 4),
            "probabilities": {
                risk_labels.get(i + label_offset, str(i + label_offset)): round(float(p), 4)
                for i, p in enumerate(probs)
            },
        }
