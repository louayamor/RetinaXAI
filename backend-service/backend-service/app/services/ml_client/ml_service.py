import base64
from pathlib import Path

import httpx

from app.core.config import settings
from app.core.exceptions import ServiceUnavailableException, UnprocessableEntityException
from app.services.ml_client.schemas import MLPredictRequest, MLPredictResponse


def _encode_image(file_path: str) -> str:
    return base64.b64encode(Path(file_path).read_bytes()).decode("utf-8")


class MLServiceClient:
    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.timeout = settings.ML_SERVICE_TIMEOUT
        self.headers = {
            "Authorization": f"Bearer {settings.ML_SERVICE_API_KEY}",
            "Content-Type": "application/json",
        }

    async def predict(self, request: MLPredictRequest) -> MLPredictResponse:
        payload = request.model_dump()
        payload["left_scan"] = _encode_image(request.left_scan_path)
        payload["right_scan"] = _encode_image(request.right_scan_path)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/predict",
                    json=payload,
                    headers=self.headers,
                )
                if response.status_code == 422:
                    raise UnprocessableEntityException(
                        response.json().get("detail", "Invalid input payload.")
                    )
                response.raise_for_status()
                return MLPredictResponse(**response.json())
        except httpx.TimeoutException:
            raise ServiceUnavailableException("ml-service")
        except httpx.ConnectError:
            raise ServiceUnavailableException("ml-service")


ml_client = MLServiceClient()