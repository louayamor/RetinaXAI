import os
from pathlib import Path

import mlflow
from loguru import logger

os.chdir(Path(__file__).parent)

from app.pipeline.dl_training_pipeline import DLTrainingPipeline
from app.pipeline.ml_training_pipeline import MLTrainingPipeline
from app.config.configuration import ConfigurationManager


def configure_mlflow():
    dagshub_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if not dagshub_uri:
        raise EnvironmentError("MLFLOW_TRACKING_URI is not set")
    mlflow.set_tracking_uri(dagshub_uri)
    mlflow.set_experiment("retinaxai-dr-classification")
    logger.info(f"mlflow tracking URI: {dagshub_uri}")


def run_ingestion_only():
    logger.info("running data ingestion only")
    manager = ConfigurationManager()
    cfg = manager.get_data_ingestion_config()

    from app.components.data_ingestion import DataIngestion
    summary = DataIngestion(cfg).run()

    logger.info(f"ingestion summary: {summary}")
    return summary


if __name__ == "__main__":
    import argparse

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

    configure_mlflow()

    if args.stage == "ingest":
        run_ingestion_only()

    elif args.stage == "all":
        if args.pipeline == "dl":
            DLTrainingPipeline(ConfigurationManager()).run()
        elif args.pipeline == "ml":
            MLTrainingPipeline(ConfigurationManager()).run()
        else:
            manager = ConfigurationManager()
            DLTrainingPipeline(manager).run()
            MLTrainingPipeline(manager).run()

    elif args.stage == "preprocess":
        manager = ConfigurationManager()
        if args.pipeline in ("dl", "both"):
            DLTrainingPipeline(manager).run_stage_2()
        if args.pipeline in ("ml", "both"):
            MLTrainingPipeline(manager).run_stage_2()

    elif args.stage == "train":
        manager = ConfigurationManager()
        if args.pipeline in ("dl", "both"):
            DLTrainingPipeline(manager).run_stage_3()
        if args.pipeline in ("ml", "both"):
            MLTrainingPipeline(manager).run_stage_3()

    elif args.stage == "evaluate":
        manager = ConfigurationManager()
        if args.pipeline in ("dl", "both"):
            DLTrainingPipeline(manager).run_stage_4()
        if args.pipeline in ("ml", "both"):
            MLTrainingPipeline(manager).run_stage_4()