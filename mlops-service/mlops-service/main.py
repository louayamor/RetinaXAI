import os
from pathlib import Path
from typing import Callable, Dict

import argparse
import dagshub
import mlflow
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
os.chdir(Path(__file__).parent)

from app.pipeline.imaging.stage_01_data_ingestion import run as img_ingest
from app.pipeline.imaging.stage_02_data_cleaning import run as img_clean
from app.pipeline.imaging.stage_03_data_transformation import run as img_transform
from app.pipeline.imaging.stage_04_model_trainer import run as img_train
from app.pipeline.imaging.stage_05_model_evaluation import run as img_evaluate

from app.pipeline.clinical.stage_01_data_ingestion import run as clin_ingest
from app.pipeline.clinical.stage_02_data_cleaning import run as clin_clean
from app.pipeline.clinical.stage_03_data_transformation import run as clin_transform
from app.pipeline.clinical.stage_04_model_trainer import run as clin_train
from app.pipeline.clinical.stage_05_model_evaluation import run as clin_evaluate

IMAGING_PIPELINE: Dict[str, Callable] = {
    "ingest": img_ingest,
    "clean": img_clean,
    "transform": img_transform,
    "train": img_train,
    "evaluate": img_evaluate,
}

CLINICAL_PIPELINE: Dict[str, Callable] = {
    "ingest": clin_ingest,
    "clean": clin_clean,
    "transform": clin_transform,
    "train": clin_train,
    "evaluate": clin_evaluate,
}

PIPELINE_ORDER = ["ingest", "clean", "transform", "train", "evaluate"]

def configure_mlflow() -> None:
    dagshub.init(
        repo_owner="louayamor",
        repo_name="retinaxai",
        mlflow=True,
    )
    mlflow.set_experiment("retinaxai-dr-classification")
    logger.info("MLflow configured via DagsHub")

def run_stage(stage: str, pipeline: Dict[str, Callable]) -> None:
    if stage not in pipeline:
        raise ValueError(f"Invalid stage: {stage}")
    logger.info(f"Running stage: {stage}")
    pipeline[stage]()


def run_full_pipeline(pipeline: Dict[str, Callable]) -> None:
    for stage in PIPELINE_ORDER:
        run_stage(stage, pipeline)


def run_pipeline(stage: str, target: str) -> None:
    if stage in ("train", "evaluate", "all"):
        configure_mlflow()

    targets = []
    if target in ("imaging", "both"):
        targets.append(("imaging", IMAGING_PIPELINE))
    if target in ("clinical", "both"):
        targets.append(("clinical", CLINICAL_PIPELINE))

    for name, pipe in targets:
        logger.info(f"Executing {name} pipeline")

        if stage == "all":
            run_full_pipeline(pipe)
        else:
            run_stage(stage, pipe)

def serve() -> None:
    import uvicorn
    from app.api.app import app
    from app.config.settings import Settings

    settings = Settings()

    logger.info(
        f"Starting API server at {settings.app_host}:{settings.app_port}"
    )

    uvicorn.run(
        "app.api.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )

def main():
    parser = argparse.ArgumentParser(description="RetinaXAI MLOps Service")

    subparsers = parser.add_subparsers(dest="command", required=True)

    pipeline_parser = subparsers.add_parser("pipeline")
    pipeline_parser.add_argument(
        "--stage",
        type=str,
        choices=["ingest", "clean", "transform", "train", "evaluate", "all"],
        default="all",
    )
    pipeline_parser.add_argument(
        "--pipeline",
        type=str,
        choices=["imaging", "clinical", "both"],
        default="both",
    )

    subparsers.add_parser("serve")

    args = parser.parse_args()

    if args.command == "pipeline":
        run_pipeline(args.stage, args.pipeline)

    elif args.command == "serve":
        serve()


if __name__ == "__main__":
    main()