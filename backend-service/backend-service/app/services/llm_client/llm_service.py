import httpx

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException
from app.services.llm_client.schemas import LLMReportRequest, LLMReportResponse

OLLAMA_GENERATE_ENDPOINT = "/api/generate"

REPORT_PROMPT_TEMPLATE = """
You are a medical AI assistant. Based on the following patient data and ML model prediction, generate a detailed clinical report.

Patient Information:
- Age: {patient_age}
- Gender: {patient_gender}

ML Model: {model_name} v{model_version}
Prediction Output: {prediction_output}
Confidence Score: {confidence_score:.2%}

Generate a structured report with two sections:
1. FULL REPORT: A detailed clinical interpretation of the prediction results.
2. SUMMARY: A concise 2-3 sentence summary for quick reference.

Respond in JSON format:
{{"content": "<full report>", "summary": "<summary>"}}
"""


class LLMServiceClient:
    def __init__(self):
        self.base_url = settings.LLM_SERVICE_URL
        self.timeout = settings.LLM_SERVICE_TIMEOUT
        self.model = settings.LLM_MODEL

    async def generate_report(self, request: LLMReportRequest) -> LLMReportResponse:
        prompt = REPORT_PROMPT_TEMPLATE.format(
            patient_age=request.patient_age,
            patient_gender=request.patient_gender,
            model_name=request.model_name,
            model_version=request.model_version,
            prediction_output=request.prediction_output,
            confidence_score=request.confidence_score,
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{OLLAMA_GENERATE_ENDPOINT}",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                import json
                parsed = json.loads(data["response"])
                return LLMReportResponse(
                    content=parsed["content"],
                    summary=parsed["summary"],
                    model_used=self.model,
                )
        except httpx.TimeoutException:
            raise ServiceUnavailableException("llm-service")
        except httpx.ConnectError:
            raise ServiceUnavailableException("llm-service")
        except (KeyError, ValueError):
            raise ServiceUnavailableException("llm-service")


llm_client = LLMServiceClient()