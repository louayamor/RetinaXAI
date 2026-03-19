from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from app.api.schemas import ClinicalFeatures, PredictResponse
from app.api.dependencies import get_settings
from app.config.settings import Settings
from app.services.inference_service import InferenceService
import json

router = APIRouter()
_inference_service = None


def get_inference_service(settings: Settings = Depends(get_settings)) -> InferenceService:
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService(settings)
    return _inference_service


@router.post("/predict", response_model=PredictResponse)
async def predict(
    image: UploadFile = File(...),
    clinical_features: str = Form(default="{}"),
    service: InferenceService = Depends(get_inference_service),
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="uploaded file must be an image")

    try:
        features_dict = json.loads(clinical_features)
        features = ClinicalFeatures(**features_dict)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"invalid clinical features: {e}")

    image_bytes = await image.read()

    imaging_result = service.predict_imaging(image_bytes)
    clinical_result = service.predict_clinical(features)

    return PredictResponse(
        imaging=imaging_result,
        clinical=clinical_result,
    )
