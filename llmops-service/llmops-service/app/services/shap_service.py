import json
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger

from app.core.config import settings


class ShapExplainabilityError(Exception):
    pass


class FeatureContribution:
    def __init__(
        self,
        feature_name: str,
        contribution: float,
        base_value: float,
        value: float,
    ):
        self.feature_name = feature_name
        self.contribution = contribution
        self.base_value = base_value
        self.value = value


class ShapExplanation:
    def __init__(
        self,
        model_type: str,
        expected_value: float,
        contributions: list[FeatureContribution],
        pipeline: str,
    ):
        self.model_type = model_type
        self.expected_value = expected_value
        self.contributions = contributions
        self.pipeline = pipeline

    def to_dict(self) -> dict:
        return {
            "model_type": self.model_type,
            "expected_value": self.expected_value,
            "pipeline": self.pipeline,
            "features": [
                {
                    "name": c.feature_name,
                    "contribution": c.contribution,
                    "base_value": c.base_value,
                    "value": c.value,
                }
                for c in self.contributions
            ],
            "top_positive": [
                {
                    "name": c.feature_name,
                    "contribution": c.contribution,
                }
                for c in sorted(
                    self.contributions,
                    key=lambda x: x.contribution,
                    reverse=True,
                )[:5]
            ],
            "top_negative": [
                {
                    "name": c.feature_name,
                    "contribution": c.contribution,
                }
                for c in sorted(
                    self.contributions,
                    key=lambda x: x.contribution,
                )[:5]
            ],
        }


class ShapService:
    def __init__(self):
        self.artifacts_root = settings.artifacts_root
        self._shap_values_cache: dict[str, list[dict]] = {}
        self._global_importance: dict[str, dict[str, float]] = {}

    def _load_clinical_model(self) -> Any:
        model_path = self.artifacts_root / "model" / "clinical" / "model.pkl"
        if not model_path.exists():
            raise ShapExplainabilityError(f"Clinical model not found: {model_path}")

        import pickle

        with open(model_path, "rb") as f:
            model = pickle.load(f)
        return model

    def _get_feature_names(self) -> list[str]:
        config_path = (
            self.artifacts_root / "data" / "processed" / "clinical" / "features.json"
        )
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get("features", [])

        return [
            "patient_age",
            "patient_gender",
            "thickness_center_fovea",
            "thickness_average_thickness",
            "thickness_total_volume_mm3",
            "thickness_inner_superior",
            "thickness_inner_nasal",
            "thickness_inner_inferior",
            "thickness_inner_temporal",
            "thickness_outer_superior",
            "thickness_outer_nasal",
            "thickness_outer_inferior",
            "thickness_outer_temporal",
            "clinical_edema",
            "clinical_erm_status",
        ]

    def explain_prediction(
        self,
        features: dict[str, Any],
        pipeline: str = "clinical",
    ) -> ShapExplanation:
        try:
            import shap
        except ImportError:
            raise ShapExplainabilityError("shap package not installed")

        model = self._load_clinical_model()
        feature_names = self._get_feature_names()

        feature_values = []
        for fname in feature_names:
            if fname in features:
                val = features[fname]
                if isinstance(val, (int, float)):
                    feature_values.append(float(val))
                else:
                    feature_values.append(0.0)
            else:
                feature_values.append(0.0)

        feature_array = np.array([feature_values])

        try:
            if hasattr(model, "predict_proba"):
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(feature_array)

                if isinstance(shap_values, list):
                    shap_values = shap_values[0][0]
                else:
                    shap_values = shap_values[0]

                expected_value = float(explainer.expected_value)
                if isinstance(expected_value, (np.ndarray, list, tuple)):
                    expected_value = float(expected_value[0])
                else:
                    expected_value = float(expected_value)

            else:
                raise ShapExplainabilityError("Model does not support SHAP")

        except Exception as e:
            logger.warning(f"SHAP calculation failed, using fallback: {e}")
            expected_value = 0.5
            contributions = []
            for fname, fvalue in zip(feature_names, feature_values):
                contributions.append(
                    FeatureContribution(
                        feature_name=fname,
                        contribution=0.0,
                        base_value=expected_value,
                        value=fvalue,
                    )
                )
            return ShapExplanation(
                model_type="xgboost",
                expected_value=expected_value,
                contributions=contributions,
                pipeline=pipeline,
            )

        contributions = []
        for fname, fvalue, svalue in zip(feature_names, feature_values, shap_values):
            contributions.append(
                FeatureContribution(
                    feature_name=fname,
                    contribution=float(svalue),
                    base_value=expected_value,
                    value=float(fvalue),
                )
            )

        return ShapExplanation(
            model_type="xgboost",
            expected_value=expected_value,
            contributions=contributions,
            pipeline=pipeline,
        )

    def compute_global_importance(
        self,
        test_csv: Path,
        pipeline: str = "clinical",
        sample_size: int = 100,
    ) -> dict[str, float]:
        try:
            import shap
        except ImportError:
            raise ShapExplainabilityError("shap package not installed")

        import pandas as pd

        model = self._load_clinical_model()
        df = pd.read_csv(test_csv)

        feature_names = self._get_feature_names()
        available_cols = [c for c in feature_names if c in df.columns]

        if len(available_cols) == 0:
            return {}

        X = df[available_cols].head(sample_size).values
        feature_names = available_cols

        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)

            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            else:
                shap_values = shap_values

            mean_abs_shap = np.abs(shap_values).mean(axis=0)

            importance = {}
            for fname, mval in zip(feature_names, mean_abs_shap):
                importance[fname] = float(mval)

            self._global_importance[pipeline] = importance
            logger.info(
                f"Computed global SHAP importance for {len(importance)} features"
            )

            return importance

        except Exception as e:
            logger.warning(f"Global SHAP calculation failed: {e}")
            return {}

    def get_global_importance(self, pipeline: str = "clinical") -> dict[str, float]:
        return self._global_importance.get(pipeline, {})

    def check_bias(
        self,
        test_csv: Path,
        demographic_col: str = "patient_gender",
        pipeline: str = "clinical",
    ) -> dict[str, Any]:
        import pandas as pd

        df = pd.read_csv(test_csv)

        if demographic_col not in df.columns:
            return {"error": f"Demographic column not found: {demographic_col}"}

        groups = df[demographic_col].unique()

        if len(groups) < 2:
            return {"error": "Not enough demographic groups for comparison"}

        bias_results = {}

        for group in groups:
            group_df = df[df[demographic_col] == group]
            if len(group_df) > 10:
                importance = self.compute_global_importance(test_csv, pipeline)
                bias_results[str(group)] = importance

        if len(bias_results) < 2:
            return {"error": "Insufficient data for bias check"}

        comparison = {}
        for feature in bias_results[list(bias_results.keys())[0]]:
            values = [v.get(feature, 0) for v in bias_results.values()]
            if all(v is not None for v in values):
                diff = max(values) - min(values)
                comparison[feature] = {
                    "max_diff": float(diff),
                    "potentially_biased": diff > 0.1,
                }

        return comparison


def get_shap_service() -> ShapService:
    return ShapService()
