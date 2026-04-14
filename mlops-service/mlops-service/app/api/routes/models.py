from http import HTTPStatus
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.dependencies import get_settings
from app.api.schemas import (
    ModelDetailResponse,
    ModelListResponse,
    ModelPromotionRequest,
    ModelPromotionResponse,
    ModelRegisterResponse,
    ModelRollbackRequest,
    ModelStage,
    CurrentProductionResponse,
)
from app.config.settings import Settings
from app.services.model_registry import (
    ModelRegistryError,
    ModelNotFoundError,
    ModelRegistryService,
)

router = APIRouter(prefix="/models", tags=["models"])


def get_registry_service(
    settings: Settings = Depends(get_settings),
) -> ModelRegistryService:
    """Get model registry service instance."""
    registry_dir = settings.model_registry_dir
    return ModelRegistryService(registry_dir)


@router.post(
    "/register",
    response_model=ModelRegisterResponse,
    status_code=HTTPStatus.CREATED,
    summary="Register a new model version",
)
async def register_model_version(
    version: str,
    pipeline: str,
    source_path: str,
    metrics: dict,
    metadata: Optional[dict] = None,
    settings: Settings = Depends(get_settings),
    service: ModelRegistryService = Depends(get_registry_service),
) -> ModelRegisterResponse:
    """Register a new model version in the registry.

    The model is initially placed in the 'staging' stage and can be promoted
    to production after validation.

    Args:
        version: Semantic version string (e.g., "v1.2.0")
        pipeline: Pipeline type ("imaging" or "clinical")
        source_path: Path to model artifact
        metrics: Model performance metrics
        metadata: Optional additional metadata

    Returns:
        Model registration response

    Raises:
        HTTPException: If registration fails
    """
    logger.info(f"Registering model {version} for pipeline {pipeline}")

    try:
        # Validate pipeline type
        if pipeline not in ["imaging", "clinical"]:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="pipeline must be 'imaging' or 'clinical'",
            )

        # Parse source path
        source_path_obj = Path(source_path)
        if not source_path_obj.exists():
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Source path does not exist: {source_path}",
            )

        # Register model version
        model_version = service.register_version(
            version=version,
            pipeline=pipeline,
            source_path=source_path_obj,
            metrics=metrics,
            metadata=metadata or {},
        )

        logger.info(f"Successfully registered model {version}")

        return ModelRegisterResponse(
            model=model_version,
            message=f"Model {version} registered successfully in staging",
            next_action=f"Run GET /models/{version} to view details, then POST /models/{version}/promote to deploy to production",
        )

    except ModelRegistryError as e:
        logger.error(f"Registry error: {e}")
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post(
    "/{version}/promote",
    response_model=ModelPromotionResponse,
    summary="Promote a model version to production",
)
async def promote_model(
    version: str,
    reason: Optional[str] = None,
    service: ModelRegistryService = Depends(get_registry_service),
) -> ModelPromotionResponse:
    """Promote a model version to production.

    Automatically creates a backup of the current production model
    and archives it before promoting the new version.

    Args:
        version: Version string to promote
        reason: Optional reason for promotion

    Returns:
        Promotion response with details

    Raises:
        HTTPException: If promotion fails
    """
    logger.info(f"Promoting model {version} to production")

    try:
        # Get current production model for backup info
        model_version = service.get_version(version)
        current_production = service.get_current_production(model_version.pipeline)

        previous_version = current_production.version if current_production else None

        # Promote model
        promoted = service.promote_version(
            version=version, target_stage=ModelStage.PRODUCTION, reason=reason
        )

        logger.info(f"Successfully promoted {version} to production")

        return ModelPromotionResponse(
            success=True,
            previous_version=previous_version,
            new_version=promoted.version,
            promotion_time=promoted.promoted_at,
            notes=f"Model {version} is now in production. Previous version has been archived.",
        )

    except ModelNotFoundError as e:
        logger.error(f"Model not found: {e}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Promotion failed: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Promotion failed: {str(e)}",
        )


@router.post(
    "/{version}/rollback",
    response_model=ModelPromotionResponse,
    summary="Rollback to a previous model version",
)
async def rollback_model(
    version: str,
    request: ModelRollbackRequest,
    service: ModelRegistryService = Depends(get_registry_service),
) -> ModelPromotionResponse:
    """Rollback to a previous model version.

    Archives current production model and promotes the specified
    version to production.

    Args:
        version: Version string to rollback to
        request: Rollback request with reason

    Returns:
        Rollback response

    Raises:
        HTTPException: If rollback fails
    """
    logger.info(f"Rolling back to model {version}")

    try:
        # Get current production for rollback info
        rollout_version = service.get_version(version)
        current_production = service.get_current_production(rollout_version.pipeline)

        current_version = current_production.version if current_production else None

        # Perform rollback
        rolled_back = service.rollback_version(version, request.reason)

        logger.info(f"Successfully rolled back to {version}")

        return ModelPromotionResponse(
            success=True,
            previous_version=current_version,
            new_version=rolled_back.version,
            promotion_time=rolled_back.promoted_at,
            notes=f"Rolled back from {current_version} to {version}. Reason: {request.reason}",
        )

    except ModelNotFoundError as e:
        logger.error(f"Model not found: {e}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Rollback failed: {str(e)}",
        )


@router.get("/", response_model=ModelListResponse, summary="List all model versions")
async def list_models(
    pipeline: Optional[str] = None,
    stage: Optional[ModelStage] = None,
    service: ModelRegistryService = Depends(get_registry_service),
) -> ModelListResponse:
    """List all model versions with optional filtering.

    Args:
        pipeline: Filter by pipeline ("imaging" or "clinical")
        stage: Filter by lifecycle stage

    Returns:
        List of model versions with summary statistics
    """
    try:
        # Validate pipeline filter
        if pipeline and pipeline not in ["imaging", "clinical"]:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="pipeline must be 'imaging' or 'clinical'",
            )

        models = service.list_versions(pipeline=pipeline, stage=stage)

        return ModelListResponse(
            models=models,
            total=len(models),
            staging_count=len([m for m in models if m.stage == ModelStage.STAGING]),
            production_count=len(
                [m for m in models if m.stage == ModelStage.PRODUCTION]
            ),
            archived_count=len([m for m in models if m.stage == ModelStage.ARCHIVED]),
        )

    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}",
        )


@router.get(
    "/{version}",
    response_model=ModelDetailResponse,
    summary="Get details for a specific model version",
)
async def get_model(
    version: str,
    service: ModelRegistryService = Depends(get_registry_service),
) -> ModelDetailResponse:
    """Get detailed information for a specific model version.

    Args:
        version: Version string

    Returns:
        Detailed version information

    Raises:
        HTTPException: If version not found
    """
    try:
        model = service.get_version(version)
        current_production = (
            service.get_current_production(model.pipeline) if model.pipeline else None
        )

        promotion_history = service.get_promotion_history(version)

        return ModelDetailResponse(
            model=model,
            is_current_production=(
                current_production is not None and current_production.version == version
            ),
            can_promote=(model.stage == ModelStage.STAGING),
            can_rollback=(model.stage == ModelStage.PRODUCTION),
            promotion_history=promotion_history,
        )

    except ModelNotFoundError as e:
        logger.error(f"Model not found: {e}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get model: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model: {str(e)}",
        )


@router.get(
    "/production/current",
    response_model=CurrentProductionResponse,
    summary="Get current production models",
)
async def get_current_production(
    service: ModelRegistryService = Depends(get_registry_service),
) -> CurrentProductionResponse:
    """Get the currently deployed production models for each pipeline.

    Returns:
        Current production models for imaging and clinical pipelines
    """
    try:
        imaging_model = service.get_current_production("imaging")
        clinical_model = service.get_current_production("clinical")

        return CurrentProductionResponse(
            imaging=imaging_model,
            clinical=clinical_model,
            promoted_at=(imaging_model.promoted_at if imaging_model else None),
        )

    except Exception as e:
        logger.error(f"Failed to get production models: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Failed to get production models: {str(e)}",
        )


@router.post(
    "/{version}/stage", summary="Move model to staging (default initial stage)"
)
async def stage_model(
    version: str,
    service: ModelRegistryService = Depends(get_registry_service),
) -> JSONResponse:
    """Re-stage an archived or production model back to staging.

    Useful for testing or re-validation before re-promoting.

    Args:
        version: Model version to stage

    Returns:
        Success confirmation
    """
    try:
        model = service.promote_version(
            version, ModelStage.STAGING, reason="Re-staging for testing"
        )

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={
                "success": True,
                "version": version,
                "stage": ModelStage.STAGING.value,
                "message": f"Model {version} moved to staging",
            },
        )

    except ModelNotFoundError as e:
        logger.error(f"Model not found: {e}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Staging failed: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Staging failed: {str(e)}",
        )
