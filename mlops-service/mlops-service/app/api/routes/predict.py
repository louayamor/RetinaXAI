import base64
import io

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from PIL import Image

from app.api.dependencies import get_settings
from app.api.schemas import ClinicalFeatures, MLPredictHttpRequest, PredictResponse
from app.config.settings import Settings
from app.services.inference_service import InferenceService

router = APIRouter()
_inference_service = None


def get_inference_service(settings: Settings = Depends(get_settings)) -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService(settings)
    return _inference_service


def _decode_base64_image(base64_str: str) -> bytes:
    try:
        return base64.b64decode(base64_str, validate=True)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"invalid base64 image: {e}")


def _validate_image_bytes(image_bytes: bytes) -> None:
    try:
        Image.open(io.BytesIO(image_bytes)).verify()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"invalid image data: {e}")


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: MLPredictHttpRequest,
    service: InferenceService = Depends(get_inference_service),
) -> PredictResponse:
    try:
        left_bytes = _decode_base64_image(request.left_scan)
        right_bytes = _decode_base64_image(request.right_scan)
        _validate_image_bytes(left_bytes)
        _validate_image_bytes(right_bytes)
        
        logger.info(
            f"processing prediction for {request.patient_gender} "
            f"age {request.patient_age}"
        )
        
        left_imaging_result = service.predict_imaging(left_bytes)
        right_imaging_result = service.predict_imaging(right_bytes)
        
        try:
            features = ClinicalFeatures(**request.features)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"invalid clinical features: {e}"
            )
        
        clinical_result = service.predict_clinical(features)
        
        left_imaging_result["right_eye_prediction"] = right_imaging_result
        left_imaging_result["clinical_risk"] = clinical_result.get("predicted_grade")
        left_imaging_result["clinical_risk_score"] = clinical_result.get("risk_score")
        
        logger.info(
            f"prediction complete: left={left_imaging_result['predicted_grade']} "
            f"right={right_imaging_result['predicted_grade']} "
            f"left_confidence={left_imaging_result['confidence']}"
        )
        
        return PredictResponse(
            prediction=left_imaging_result,
            confidence_score=left_imaging_result["confidence"],
            model_name=request.model_name,
            model_version=request.model_version,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"prediction failed: {e}")
