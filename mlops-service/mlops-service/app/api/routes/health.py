from fastapi import APIRouter
from app.api.schemas import HealthResponse
from app.api.dependencies import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
    )
