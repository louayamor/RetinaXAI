import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

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

_JOB_FILE = Path("artifacts/training_jobs.json")
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
    _job_store[job_id]["status"] = "running"
    _job_store[job_id]["started_at"] = datetime.utcnow().isoformat()
    _save_jobs()

    TRAINING_RUNS_TOTAL.labels(pipeline=pipeline).inc()
    ACTIVE_TRAINING_JOBS.inc()

    logger.info(f"pipeline job started: job_id={job_id} pipeline={pipeline}")

    try:
        _configure_mlflow()

        if pipeline in ("imaging", "both"):
            img_s1()
            img_s2()
            img_s3()
            img_s4()
            img_s5()

        if pipeline in ("clinical", "both"):
            clin_s1()
            clin_s2()
            clin_s3()
            clin_s4()
            clin_s5()

        _job_store[job_id]["status"] = "completed"
        _job_store[job_id]["completed_at"] = datetime.utcnow().isoformat()
        _save_jobs()
        logger.info(f"pipeline job completed: job_id={job_id}")

    except Exception as e:
        _job_store[job_id]["status"] = "failed"
        _job_store[job_id]["error"] = str(e)
        _job_store[job_id]["completed_at"] = datetime.utcnow().isoformat()
        _save_jobs()
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
