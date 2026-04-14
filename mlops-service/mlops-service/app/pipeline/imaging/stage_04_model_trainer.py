from pathlib import Path
from loguru import logger
from app.config.configuration import ConfigurationManager
from app.components.imaging.model_trainer import ImagingModelTrainer
from app.components.imaging.data_transformation import create_fine_tune_split
import pandas as pd


def run(phase: str = "phase1", checkpoint_path: Path | None = None):
    logger.info(f">>> stage 04: imaging model training started (phase={phase})")
    manager = ConfigurationManager()
    cfg = manager.get_imaging_model_trainer_config()
    transformation_cfg = manager.get_imaging_transformation_config()
    logger.info(
        f"stage 04 config: model={cfg.model_name}, pretrained={cfg.pretrained}, checkpoint={cfg.checkpoint_path}, train_csv={transformation_cfg.train_csv}, test_csv={transformation_cfg.test_csv}"
    )

    custom_train_csv = None
    if phase == "phase2" and checkpoint_path:
        logger.info("Creating Phase 2 fine-tuning dataset")
        try:
            samaya_csv = transformation_cfg.samaya_csv
            if samaya_csv.exists():
                samaya_df = pd.read_csv(samaya_csv)
                eyepacs_df = pd.read_csv(transformation_cfg.train_csv)
                fine_tune_df = create_fine_tune_split(
                    samaya_df, eyepacs_df, clinical_ratio=0.7, no_dr_ratio=0.25
                )
                temp_csv = transformation_cfg.train_csv.parent / "train_phase2.csv"
                fine_tune_df.to_csv(temp_csv, index=False)
                custom_train_csv = temp_csv
                logger.info(f"Phase 2 training data: {len(fine_tune_df)} samples")
            else:
                logger.warning(
                    f"samaya CSV not found: {samaya_csv}, falling back to phase1"
                )
                phase = "phase1"
        except Exception as e:
            logger.warning(
                f"Failed to create Phase 2 dataset: {e}, falling back to phase1"
            )
            phase = "phase1"

    final_checkpoint = ImagingModelTrainer(
        cfg,
        transformation_cfg,
        phase=phase,
        load_checkpoint=checkpoint_path,
        custom_train_csv=custom_train_csv,
    ).train()

    logger.info(
        f">>> stage 04: imaging model training complete (phase={phase}, checkpoint={final_checkpoint})"
    )
    return final_checkpoint


if __name__ == "__main__":
    run()
