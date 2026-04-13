from __future__ import annotations

from loguru import logger

from app.core.config import settings
from app.llm.client import get_llm_client
from app.prompts.templates import REPORT_SYSTEM_PROMPT
from app.services.websocket_client import send_xai_event


class XAIPipeline:
    _instance: "XAIPipeline | None" = None

    def __new__(cls) -> "XAIPipeline":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        provider = (
            settings.llm_provider.value
            if hasattr(settings.llm_provider, "value")
            else str(settings.llm_provider)
        )
        token = settings.github_token if provider == "github" else settings.llm_api_key
        base_url = (
            settings.github_endpoint if provider == "github" else settings.llm_base_url
        )

        timeout = settings.timeout_seconds

        client_kwargs: dict[str, str | int] = {
            "model": settings.llm_model,
            "timeout_seconds": timeout,
        }
        if provider == "github":
            client_kwargs["token"] = token if token is not None else ""
            client_kwargs["endpoint"] = base_url if base_url is not None else ""
        elif provider == "ollama":
            client_kwargs["base_url"] = (
                base_url if base_url is not None else settings.ollama_base_url
            )
        else:
            client_kwargs["token"] = token if token is not None else ""
            client_kwargs["base_url"] = base_url if base_url is not None else ""

        self.client = get_llm_client(provider, **client_kwargs)
        self._initialized = True
        logger.info("XAI Pipeline initialized")

    async def explain_prediction(
        self,
        prediction_id: str,
        dr_grade: str,
        confidence: float,
        clinical_features: dict | None = None,
    ) -> dict:
        """Generate natural language explanation of DR prediction."""
        await send_xai_event(
            event="xai.prediction",
            stage="prediction",
            status="started",
            progress=0,
            message="Generating prediction explanation...",
            prediction_id=prediction_id,
        )

        try:
            prompt = self._build_prediction_prompt(
                dr_grade, confidence, clinical_features
            )
            response = self.client.invoke(prompt)

            await send_xai_event(
                event="xai.prediction",
                stage="prediction",
                status="completed",
                progress=100,
                message="Prediction explanation generated",
                prediction_id=prediction_id,
                details={"dr_grade": dr_grade, "confidence": confidence},
            )

            return {
                "content": response,
                "summary": response[:500],
                "model_used": settings.llm_model,
                "status": "completed",
            }
        except Exception as e:
            await send_xai_event(
                event="xai.prediction",
                stage="prediction",
                status="failed",
                progress=0,
                message=str(e),
                prediction_id=prediction_id,
                error=str(e),
            )
            raise

    async def explain_gradcam(
        self,
        prediction_id: str,
        left_eye_regions: list[str],
        right_eye_regions: list[str],
    ) -> dict:
        """Interpret highlighted regions in GradCAM heatmaps."""
        await send_xai_event(
            event="xai.gradcam",
            stage="gradcam",
            status="started",
            progress=0,
            message="Interpreting GradCAM regions...",
            prediction_id=prediction_id,
        )

        try:
            prompt = self._build_gradcam_prompt(left_eye_regions, right_eye_regions)
            response = self.client.invoke(prompt)

            highlighted_regions = {
                "left_eye": left_eye_regions,
                "right_eye": right_eye_regions,
            }

            await send_xai_event(
                event="xai.gradcam",
                stage="gradcam",
                status="completed",
                progress=100,
                message="GradCAM interpretation complete",
                prediction_id=prediction_id,
                details={
                    "left_regions": len(left_eye_regions),
                    "right_regions": len(right_eye_regions),
                },
            )

            return {
                "left_eye_explanation": response,
                "right_eye_explanation": response,
                "highlighted_regions": highlighted_regions,
                "model_used": settings.llm_model,
            }
        except Exception as e:
            await send_xai_event(
                event="xai.gradcam",
                stage="gradcam",
                status="failed",
                progress=0,
                message=str(e),
                prediction_id=prediction_id,
                error=str(e),
            )
            raise

    async def generate_severity_report(
        self,
        prediction_id: str,
        patient_data: dict,
        dr_grade: str,
        risk_factors: list[str],
    ) -> dict:
        """Generate clinical severity report with risk level and recommendations."""
        await send_xai_event(
            event="xai.severity",
            stage="severity",
            status="started",
            progress=0,
            message="Generating severity report...",
            prediction_id=prediction_id,
        )

        try:
            prompt = self._build_severity_prompt(patient_data, dr_grade, risk_factors)
            response = self.client.invoke(prompt)

            risk_level = self._determine_risk_level(dr_grade)
            recommendations = self._generate_recommendations(dr_grade, risk_factors)

            await send_xai_event(
                event="xai.severity",
                stage="severity",
                status="completed",
                progress=100,
                message="Severity report generated",
                prediction_id=prediction_id,
                details={"risk_level": risk_level},
            )

            return {
                "content": response,
                "summary": response[:500],
                "risk_level": risk_level,
                "recommendations": recommendations,
                "model_used": settings.llm_model,
            }
        except Exception as e:
            await send_xai_event(
                event="xai.severity",
                stage="severity",
                status="failed",
                progress=0,
                message=str(e),
                prediction_id=prediction_id,
                error=str(e),
            )
            raise

    def _build_prediction_prompt(
        self,
        dr_grade: str,
        confidence: float,
        clinical_features: dict | None,
    ) -> str:
        base = f"""Explain this diabetic retinopathy prediction in patient-friendly terms:
- DR Grade: {dr_grade}
- Confidence: {confidence:.1%}

{f"Clinical context: {clinical_features}" if clinical_features else ""}"""

        return f"{REPORT_SYSTEM_PROMPT}\n\n{base}"

    def _build_gradcam_prompt(
        self,
        left_regions: list[str],
        right_regions: list[str],
    ) -> str:
        return f"""Interpret these highlighted regions from GradCAM heatmaps:

Left Eye: {", ".join(left_regions)}
Right Eye: {", ".join(right_regions)}

Explain what these regions indicate for DR diagnosis."""

    def _build_severity_prompt(
        self,
        patient_data: dict,
        dr_grade: str,
        risk_factors: list[str],
    ) -> str:
        return f"""Generate a clinical severity report for this patient:

Patient: {patient_data.get("name", "Unknown")}
DR Grade: {dr_grade}
Risk Factors: {", ".join(risk_factors)}

Provide a professional clinical assessment with risk level and recommendations."""

    def _determine_risk_level(self, dr_grade: str) -> str:
        mapping = {
            "No DR": "low",
            "Mild": "low",
            "Moderate": "moderate",
            "Severe": "high",
            "Proliferative DR": "severe",
        }
        return mapping.get(dr_grade, "moderate")

    def _generate_recommendations(
        self, dr_grade: str, risk_factors: list[str]
    ) -> list[str]:
        recommendations = []

        if dr_grade in ("Mild", "No DR"):
            recommendations.extend(
                [
                    "Annual retinal screening",
                    "Maintain blood sugar control",
                ]
            )
        elif dr_grade == "Moderate":
            recommendations.extend(
                [
                    "Screen every 6 months",
                    "Consider laser therapy consultation",
                ]
            )
        elif dr_grade == "Severe":
            recommendations.extend(
                [
                    "Immediate ophthalmology referral",
                    "Consider laser therapy",
                ]
            )
        elif dr_grade == "Proliferative DR":
            recommendations.extend(
                [
                    "Urgent vitrectomy consultation",
                    "Surgical intervention required",
                ]
            )

        if "hypertension" in risk_factors:
            recommendations.append("Blood pressure management")
        if "gestational_diabetes" in risk_factors:
            recommendations.append("Post-partum follow-up")

        return recommendations


def get_xai_pipeline() -> XAIPipeline:
    return XAIPipeline()
