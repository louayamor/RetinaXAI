from loguru import logger
from pathlib import Path
from app.constants import PARAMS_FILE_PATH
from app.utils.common import read_yaml
from app.pipeline.imaging.stage_01_data_ingestion import run as imaging_ingest
from app.pipeline.imaging.stage_02_data_cleaning import run as imaging_clean
from app.pipeline.imaging.stage_03_data_transformation import run as imaging_transform
from app.pipeline.imaging.stage_04_model_trainer import run as imaging_train
from app.pipeline.imaging.stage_05_model_evaluation import run as imaging_evaluate
from app.pipeline.clinical.stage_01_data_ingestion import run as clinical_ingest
from app.pipeline.clinical.stage_02_data_cleaning import run as clinical_clean
from app.pipeline.clinical.stage_03_data_transformation import run as clinical_transform
from app.pipeline.clinical.stage_04_model_trainer import run as clinical_train
from app.pipeline.clinical.stage_05_model_evaluation import run as clinical_evaluate


class TrainingPipeline:
    def run_imaging(self):
        logger.info("=== imaging pipeline started ===")
        imaging_ingest()
        imaging_clean()
        imaging_transform()
        imaging_train()
        imaging_evaluate()
        logger.info("=== imaging pipeline complete ===")

    def run_clinical(self):
        logger.info("=== clinical pipeline started ===")
        clinical_ingest()
        clinical_clean()
        clinical_transform()
        clinical_train()
        clinical_evaluate()
        logger.info("=== clinical pipeline complete ===")

    def run_imaging_phase_based(self):
        """Run imaging training with 2-phase approach for domain adaptation."""
        logger.info("=== imaging phase-based training started ===")

        imaging_ingest()
        imaging_clean()
        imaging_transform()

        params = read_yaml(PARAMS_FILE_PATH)
        phase_cfg = params.get("phase_based_training", {})
        phase1_epochs = phase_cfg.get("phase1_epochs", 20)
        phase2_epochs = phase_cfg.get("phase2_epochs", 5)

        logger.info(f">>> Phase 1: Full eyepacs training ({phase1_epochs} epochs)")
        phase1_checkpoint = imaging_train(phase="phase1", checkpoint_path=None)

        logger.info(f">>> Phase 2: Clinical fine-tuning ({phase2_epochs} epochs)")
        phase2_checkpoint = imaging_train(
            phase="phase2", checkpoint_path=phase1_checkpoint
        )

        logger.info(">>> Running evaluation on final model")
        imaging_evaluate()

        logger.info("=== imaging phase-based training complete ===")
        return phase2_checkpoint

    def run(self):
        logger.info("=== unified training pipeline started ===")
        self.run_imaging()
        self.run_clinical()
        logger.info("=== unified training pipeline complete ===")
