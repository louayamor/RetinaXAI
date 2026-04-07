import json

import httpx

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException
from app.services.llm_client.schemas import LLMReportRequest, LLMReportResponse

OLLAMA_GENERATE_ENDPOINT = "/api/generate"


class LLMServiceClient:
    def __init__(self):
        self.base_url = settings.LLM_SERVICE_URL
        self.timeout = settings.LLM_SERVICE_TIMEOUT
        self.model = settings.LLM_MODEL

    async def generate_report(self, request: LLMReportRequest) -> LLMReportResponse:
        payload = {
            "model": self.model,
            "patient": request.patient,
            "prediction": request.prediction,
            "cleaned_summary": request.cleaned_summary,
            "raw_ocr_text": request.raw_ocr_text,
            "report_type": request.report_type,
            "language": request.language,
            "tone": request.tone,
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
                parsed = json.loads(data["response"])
                return LLMReportResponse(
                    content=parsed["content"],
                    summary=parsed["summary"],
                    model_used=parsed.get("model_used", self.model),
                )
        except httpx.TimeoutException:
            raise ServiceUnavailableException("llm-service")
        except httpx.ConnectError:
            raise ServiceUnavailableException("llm-service")
        except (KeyError, ValueError):
            raise ServiceUnavailableException("llm-service")


llm_client = LLMServiceClient()
