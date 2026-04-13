import json
import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger
import threading

import dagshub
import mlflow

from app.pipeline.imaging.stage_01_data_ingestion import run as img_s1
from app.pipeline.imaging.stage_02_data_cleaning import run as img_s2
from app.pipeline.imaging.stage_03_data_transformation import run as img_s3
from app.pipeline.imaging.stage_04_model_trainer import run as img_s4
from app.pipeline.imaging.stage_05_model_evaluation import run as img_s5
from app.pipeline.clinical.stage_01_data_ingestion import run as clin_s1
from app.pipeline.clinical.stage_02_data_cleaning import run as clin_s2
from app.pipeline.clinical.stage_03_data_transformation import run as clin_s3
from app.pipeline.clinical.stage_04_model_trainer import run as clin_s4
from app.pipeline.clinical.stage_05_model_evaluation import run as clin_s5

from monitoring.prometheus_metrics import (
    TRAINING_RUNS_TOTAL,
    ACTIVE_TRAINING_JOBS,
)

try:
    from app.services.websocket_client import get_websocket_client

    _ws_client = get_websocket_client()
except ImportError:
    _ws_client = None
    logger.warning("WebSocket client not available, skipping real-time events")


def _emit_stage_event(
    job_id: str,
    pipeline: str,
    stage: str,
    status: str,
    progress: int,
    message: str | None = None,
    metrics: dict[str, float] | None = None,
    error: str | None = None,
) -> None:
    """Emit training stage event to connected clients."""
    if _ws_client is None:
        return

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            _ws_client.send_training_event(
                job_id=job_id,
                pipeline=pipeline,
                stage=stage,
                status=status,
                progress=progress,
                message=message,
                metrics=metrics,
                error=error,
            )
        )
        loop.close()
    except Exception as e:
        logger.warning(f"Failed to emit WebSocket event: {e}")


_JOB_FILE = Path(os.environ.get("TRAINING_JOBS_FILE", "artifacts/training_jobs.json"))
_job_store: dict = {}


def _load_jobs() -> dict:
    global _job_store
    if _JOB_FILE.exists():
        try:
            with open(_JOB_FILE) as f:
                _job_store = json.load(f)
        except Exception:
            _job_store = {}
    return _job_store


def _save_jobs() -> None:
    _JOB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_JOB_FILE, "w") as f:
        json.dump(_job_store, f, indent=2)


_load_jobs()


def get_job_status(job_id: str) -> Optional[dict]:
    return _job_store.get(job_id)


def get_latest_job() -> Optional[dict]:
    if not _job_store:
        return None
    return list(_job_store.values())[-1]


def _configure_mlflow() -> None:
    dagshub.init(
        repo_owner="louayamor",
        repo_name="retinaxai",
        mlflow=True,
    )
    mlflow.set_experiment("retinaxai-dr-classification")
    logger.info("mlflow configured in background task")


def run_pipeline_task(job_id: str, pipeline: str) -> None:
    # Check if job was cancelled before starting
    if is_job_cancelled(job_id):
        logger.info(f"Job {job_id} was cancelled before starting")
        return

    _job_store[job_id]["status"] = "running"
    _job_store[job_id]["started_at"] = datetime.utcnow().isoformat()
    _save_jobs()

    TRAINING_RUNS_TOTAL.labels(pipeline=pipeline).inc()
    ACTIVE_TRAINING_JOBS.inc()

    logger.info(f"pipeline job started: job_id={job_id} pipeline={pipeline}")

    _emit_stage_event(
        job_id, pipeline, "pipeline", "started", 0, "Training pipeline started"
    )

    try:
        _configure_mlflow()

        if pipeline in ("imaging", "both"):
            _emit_stage_event(
                job_id,
                pipeline,
                "data_ingestion",
                "started",
                0,
                "Starting data ingestion...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                img_s1()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_ingestion",
                    "completed",
                    100,
                    "Data ingestion complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_ingestion",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "data_cleaning",
                "started",
                0,
                "Starting data cleaning...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                img_s2()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_cleaning",
                    "completed",
                    100,
                    "Data cleaning complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id, pipeline, "data_cleaning", "failed", 0, str(e), error=str(e)
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "data_transformation",
                "started",
                0,
                "Starting data transformation...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                img_s3()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_transformation",
                    "completed",
                    100,
                    "Data transformation complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_transformation",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "model_training",
                "started",
                0,
                "Starting model training...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                img_s4()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_training",
                    "completed",
                    100,
                    "Model training complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_training",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "model_evaluation",
                "started",
                0,
                "Starting model evaluation...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                img_s5()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_evaluation",
                    "completed",
                    100,
                    "Model evaluation complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_evaluation",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

        if pipeline in ("clinical", "both"):
            _emit_stage_event(
                job_id,
                pipeline,
                "data_ingestion",
                "started",
                0,
                "Starting clinical data ingestion...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                clin_s1()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_ingestion",
                    "completed",
                    100,
                    "Clinical data ingestion complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_ingestion",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "data_cleaning",
                "started",
                0,
                "Starting clinical data cleaning...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                clin_s2()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_cleaning",
                    "completed",
                    100,
                    "Clinical data cleaning complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id, pipeline, "data_cleaning", "failed", 0, str(e), error=str(e)
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "data_transformation",
                "started",
                0,
                "Starting clinical data transformation...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                clin_s3()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_transformation",
                    "completed",
                    100,
                    "Clinical data transformation complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "data_transformation",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "model_training",
                "started",
                0,
                "Starting clinical model training...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                clin_s4()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_training",
                    "completed",
                    100,
                    "Clinical model training complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_training",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

            _emit_stage_event(
                job_id,
                pipeline,
                "model_evaluation",
                "started",
                0,
                "Starting clinical model evaluation...",
            )
            if is_job_cancelled(job_id):
                raise Exception("Job cancelled by user")
            try:
                clin_s5()
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_evaluation",
                    "completed",
                    100,
                    "Clinical model evaluation complete",
                )
            except Exception as e:
                _emit_stage_event(
                    job_id,
                    pipeline,
                    "model_evaluation",
                    "failed",
                    0,
                    str(e),
                    error=str(e),
                )
                raise

        _job_store[job_id]["status"] = "completed"
        _job_store[job_id]["completed_at"] = datetime.utcnow().isoformat()
        _save_jobs()
        _emit_stage_event(
            job_id,
            pipeline,
            "pipeline",
            "completed",
            100,
            "Training pipeline completed successfully",
        )
        logger.info(f"pipeline job completed: job_id={job_id}")

    except Exception as e:
        _job_store[job_id]["status"] = "failed"
        _job_store[job_id]["error"] = str(e)
        _job_store[job_id]["completed_at"] = datetime.utcnow().isoformat()
        _save_jobs()
        _emit_stage_event(
            job_id, pipeline, "pipeline", "failed", 0, str(e), error=str(e)
        )
        logger.error(f"pipeline job failed: job_id={job_id} error={e}")

    finally:
        ACTIVE_TRAINING_JOBS.dec()


def create_job(pipeline: str) -> str:
    job_id = str(uuid.uuid4())
    _job_store[job_id] = {
        "job_id": job_id,
        "pipeline": pipeline,
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "error": None,
    }
    _save_jobs()
    return job_id


def cancel_job(job_id: str) -> bool:
    """Cancel a running job by setting status to cancelled."""
    if job_id not in _job_store:
        return False
    _job_store[job_id]["status"] = "cancelled"
    _job_store[job_id]["completed_at"] = datetime.utcnow().isoformat()
    _job_store[job_id]["error"] = "Cancelled by user"
    _save_jobs()
    logger.info(f"Job {job_id} marked as cancelled")
    return True


def is_job_cancelled(job_id: str) -> bool:
    """Check if a job has been cancelled."""
    job = _job_store.get(job_id)
    return job is not None and job.get("status") == "cancelled"
