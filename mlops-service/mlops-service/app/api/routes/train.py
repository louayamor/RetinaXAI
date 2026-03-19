from fastapi import APIRouter, BackgroundTasks, Depends
from app.api.schemas import TrainRequest, TrainResponse
from app.api.dependencies import get_settings
from app.config.settings import Settings
from app.services.training_service import create_job, run_pipeline_task

router = APIRouter()


@router.post("/train", response_model=TrainResponse)
def trigger_full_pipeline(
    request: TrainRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
):
    job_id = create_job(request.pipeline.value)
    background_tasks.add_task(run_pipeline_task, job_id, request.pipeline.value)
    return TrainResponse(
        job_id=job_id,
        pipeline=request.pipeline.value,
        status="pending",
        message=f"training job queued for pipeline: {request.pipeline.value}",
    )


@router.post("/train/imaging", response_model=TrainResponse)
def trigger_imaging_pipeline(
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
):
    job_id = create_job("imaging")
    background_tasks.add_task(run_pipeline_task, job_id, "imaging")
    return TrainResponse(
        job_id=job_id,
        pipeline="imaging",
        status="pending",
        message="imaging training job queued",
    )


@router.post("/train/clinical", response_model=TrainResponse)
def trigger_clinical_pipeline(
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
):
    job_id = create_job("clinical")
    background_tasks.add_task(run_pipeline_task, job_id, "clinical")
    return TrainResponse(
        job_id=job_id,
        pipeline="clinical",
        status="pending",
        message="clinical training job queued",
    )
