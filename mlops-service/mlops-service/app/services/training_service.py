import uuid
from datetime import datetime
from typing import Optional
from loguru import logger
import dagshub
import mlflow
import os

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


_job_store: dict = {}


def get_job_status(job_id: str) -> Optional[dict]:
    return _job_store.get(job_id)

def _configure_mlflow() -> None:
    dagshub.init(
        repo_owner="louayamor",
        repo_name="retinaxai",
        mlflow=True,
    )
    mlflow.set_experiment("retinaxai-dr-classification")
    logger.info("MLflow configured in background task")

def run_pipeline_task(job_id: str, pipeline: str) -> None:
    _job_store[job_id]["status"] = "running"
    _job_store[job_id]["started_at"] = datetime.utcnow().isoformat()
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
        logger.info(f"pipeline job completed: job_id={job_id}")

    except Exception as e:
        _job_store[job_id]["status"] = "failed"
        _job_store[job_id]["error"] = str(e)
        _job_store[job_id]["completed_at"] = datetime.utcnow().isoformat()
        logger.error(f"pipeline job failed: job_id={job_id} error={e}")


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
    return job_id
