import argparse
import os
from pathlib import Path

import dagshub
import mlflow
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
os.chdir(Path(__file__).parent)

from app.config.configuration import ConfigurationManager
from app.pipeline.dl_training_pipeline import DLTrainingPipeline
from app.pipeline.ml_training_pipeline import MLTrainingPipeline


def configure_mlflow():
    dagshub.init(
        repo_owner="louayamor",
        repo_name="retinaxai",
        mlflow=True,
    )
    mlflow.set_experiment("retinaxai-dr-classification")
    logger.info("mlflow configured via dagshub")


def run_ingestion(manager: ConfigurationManager):
    from app.components.data_ingestion import DataIngestion
    cfg = manager.get_data_ingestion_config()
    summary = DataIngestion(cfg).run()
    logger.info(f"ingestion summary: {summary}")


def run_preprocess(manager: ConfigurationManager, pipeline: str):
    if pipeline in ("dl", "both"):
        DLTrainingPipeline(manager).run_stage_2()
    if pipeline in ("ml", "both"):
        MLTrainingPipeline(manager).run_stage_2()


def run_train(manager: ConfigurationManager, pipeline: str):
    if pipeline in ("dl", "both"):
        DLTrainingPipeline(manager).run_stage_3()
    if pipeline in ("ml", "both"):
        MLTrainingPipeline(manager).run_stage_3()


def run_evaluate(manager: ConfigurationManager, pipeline: str):
    if pipeline in ("dl", "both"):
        DLTrainingPipeline(manager).run_stage_4()
    if pipeline in ("ml", "both"):
        MLTrainingPipeline(manager).run_stage_4()


def run_all(manager: ConfigurationManager, pipeline: str):
    if pipeline in ("dl", "both"):
        DLTrainingPipeline(manager).run()
    if pipeline in ("ml", "both"):
        MLTrainingPipeline(manager).run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetinaXAI MLOps Service")
    parser.add_argument(
        "--stage",
        type=str,
        choices=["ingest", "preprocess", "train", "evaluate", "all"],
        default="all",
        help="pipeline stage to run",
    )
    parser.add_argument(
        "--pipeline",
        type=str,
        choices=["dl", "ml", "both"],
        default="both",
        help="which sub-pipeline to run",
    )
    args = parser.parse_args()

    if args.stage in ("train", "evaluate", "all"):
        configure_mlflow()

    manager = ConfigurationManager()

    if args.stage == "ingest":
        run_ingestion(manager)
    elif args.stage == "preprocess":
        run_preprocess(manager, args.pipeline)
    elif args.stage == "train":
        run_train(manager, args.pipeline)
    elif args.stage == "evaluate":
        run_evaluate(manager, args.pipeline)
    elif args.stage == "all":
        run_all(manager, args.pipeline)