import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction
from app.models.prediction_explanation import ExplanationStatus, PredictionExplanation
from app.models.gradcam_explanation import GradCAMExplanation
from app.models.severity_report import RiskLevel, SeverityReport

logger = logging.getLogger(__name__)

LLM_SERVICE_URL = "http://localhost:8002"


class ExplanationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def trigger_xai_for_prediction(
        self,
        prediction: Prediction,
        patient_data: dict,
    ) -> dict:
        """Trigger XAI pipeline after prediction completes."""
        import httpx

        dr_grade = prediction.output_payload.get("predicted_class", "Unknown")
        confidence = prediction.confidence_score or 0.0
        gradcam_left = prediction.output_payload.get("gradcam_left", [])
        gradcam_right = prediction.output_payload.get("gradcam_right", [])

        results = {
            "prediction_explanation": None,
            "gradcam_explanation": None,
            "severity_report": None,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            if dr_grade != "Unknown":
                try:
                    resp = await client.post(
                        f"{LLM_SERVICE_URL}/api/xai/explain",
                        json={
                            "prediction_id": str(prediction.id),
                            "dr_grade": dr_grade,
                            "confidence": confidence,
                            "clinical_features": prediction.input_payload,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        exp = PredictionExplanation(
                            id=uuid.uuid4(),
                            prediction_id=prediction.id,
                            content=data.get("content", ""),
                            summary=data.get("summary"),
                            model_used=data.get("model_used", "unknown"),
                            status=ExplanationStatus.COMPLETED,
                        )
                        self.db.add(exp)
                        results["prediction_explanation"] = exp
                        logger.info(
                            f"[EXPLAIN SERVICE] Prediction explanation created for {prediction.id}"
                        )
                except Exception as e:
                    logger.warning(f"[EXPLAIN SERVICE] XAI explain failed: {e}")

            if gradcam_left or gradcam_right:
                try:
                    resp = await client.post(
                        f"{LLM_SERVICE_URL}/api/xai/gradcam",
                        json={
                            "prediction_id": str(prediction.id),
                            "left_eye_regions": gradcam_left
                            if isinstance(gradcam_left, list)
                            else [],
                            "right_eye_regions": gradcam_right
                            if isinstance(gradcam_right, list)
                            else [],
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        gradcam_exp = GradCAMExplanation(
                            id=uuid.uuid4(),
                            prediction_id=prediction.id,
                            left_eye_explanation=data.get("left_eye_explanation", ""),
                            right_eye_explanation=data.get("right_eye_explanation", ""),
                            highlighted_regions=data.get("highlighted_regions", {}),
                            model_used=data.get("model_used", "unknown"),
                        )
                        self.db.add(gradcam_exp)
                        results["gradcam_explanation"] = gradcam_exp
                        logger.info(
                            f"[EXPLAIN SERVICE] GradCAM explanation created for {prediction.id}"
                        )
                except Exception as e:
                    logger.warning(f"[EXPLAIN SERVICE] XAI gradcam failed: {e}")

            risk_factors = prediction.input_payload.get("risk_factors", [])
            try:
                resp = await client.post(
                    f"{LLM_SERVICE_URL}/api/xai/severity",
                    json={
                        "prediction_id": str(prediction.id),
                        "patient_data": patient_data,
                        "dr_grade": dr_grade,
                        "risk_factors": risk_factors,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    risk_level = RiskLevel(data.get("risk_level", "moderate"))
                    severity = SeverityReport(
                        id=uuid.uuid4(),
                        prediction_id=prediction.id,
                        patient_id=prediction.patient_id,
                        content=data.get("content", ""),
                        summary=data.get("summary"),
                        risk_level=risk_level,
                        recommendations=data.get("recommendations", []),
                        model_used=data.get("model_used", "unknown"),
                    )
                    self.db.add(severity)
                    results["severity_report"] = severity
                    logger.info(
                        f"[EXPLAIN SERVICE] Severity report created for {prediction.id}"
                    )
            except Exception as e:
                logger.warning(f"[EXPLAIN SERVICE] XAI severity failed: {e}")

        await self.db.commit()
        return results
