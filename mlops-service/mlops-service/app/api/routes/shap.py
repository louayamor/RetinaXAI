from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel

from app.api.dependencies import get_settings
from app.config.settings import Settings
from app.services.inference.shap_service import ShapService


class ShapExplainRequest(BaseModel):
    features: dict[str, Any]
    pipeline: str = "clinical"


class ShapExplainResponse(BaseModel):
    model_type: str
    expected_value: float
    pipeline: str
    explanation: dict


class GlobalImportanceResponse(BaseModel):
    pipeline: str
    importance: dict[str, float]


class BiasCheckResponse(BaseModel):
    pipeline: str
    demographic_column: str
    results: dict[str, Any]


router = APIRouter(prefix="/shap", tags=["shap"])


def get_shap_service(
    settings: Settings = Depends(get_settings),
) -> ShapService:
    return ShapService(settings.artifacts_root)


@router.post("/explain", response_model=ShapExplainResponse)
async def explain_prediction(
    request: ShapExplainRequest,
    service: ShapService = Depends(get_shap_service),
) -> ShapExplainResponse:
    try:
        explanation = service.explain_prediction(
            features=request.features,
            pipeline=request.pipeline,
        )

        return ShapExplainResponse(
            model_type=explanation.model_type,
            expected_value=explanation.expected_value,
            pipeline=explanation.pipeline,
            explanation=explanation.to_dict(),
        )

    except Exception as e:
        logger.error(f"SHAP explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/importance/{pipeline}", response_model=GlobalImportanceResponse)
async def get_global_importance(
    pipeline: str,
    service: ShapService = Depends(get_shap_service),
) -> GlobalImportanceResponse:
    importance = service.get_global_importance(pipeline)

    return GlobalImportanceResponse(
        pipeline=pipeline,
        importance=importance,
    )


@router.post("/importance/{pipeline}/compute", response_model=GlobalImportanceResponse)
async def compute_global_importance(
    pipeline: str,
    test_path: Optional[str] = None,
    sample_size: int = 100,
    settings: Settings = Depends(get_settings),
    service: ShapService = Depends(get_shap_service),
) -> GlobalImportanceResponse:
    if test_path:
        test_csv = Path(test_path)
        if not test_csv.is_absolute():
            test_csv = settings.artifacts_root / test_path
    else:
        test_csv = (
            settings.artifacts_root / "data" / "processed" / pipeline / "test.csv"
        )

    if not test_csv.exists():
        raise HTTPException(status_code=404, detail=f"Test data not found: {test_csv}")

    importance = service.compute_global_importance(
        test_csv=test_csv,
        pipeline=pipeline,
        sample_size=sample_size,
    )

    return GlobalImportanceResponse(
        pipeline=pipeline,
        importance=importance,
    )


@router.post("/bias/{pipeline}", response_model=BiasCheckResponse)
async def check_bias(
    pipeline: str,
    demographic_column: str = "patient_gender",
    test_path: Optional[str] = None,
    settings: Settings = Depends(get_settings),
    service: ShapService = Depends(get_shap_service),
) -> BiasCheckResponse:
    if test_path:
        test_csv = Path(test_path)
        if not test_csv.is_absolute():
            test_csv = settings.artifacts_root / test_path
    else:
        test_csv = (
            settings.artifacts_root / "data" / "processed" / pipeline / "test.csv"
        )

    if not test_csv.exists():
        raise HTTPException(status_code=404, detail=f"Test data not found: {test_csv}")

    results = service.check_bias(
        test_csv=test_csv,
        demographic_col=demographic_column,
        pipeline=pipeline,
    )

    return BiasCheckResponse(
        pipeline=pipeline,
        demographic_column=demographic_column,
        results=results,
    )
