import pandas as pd
from pathlib import Path
from loguru import logger

from evidently import Report
from evidently.presets import DataDriftPreset, ClassificationPreset


class EvidentlyReportGenerator:
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _drop_non_numeric_cols(self, df: pd.DataFrame, keep: list = None) -> pd.DataFrame:
        keep = keep or []
        cols = [
            c for c in df.columns
            if c in keep or df[c].dtype in ["float64", "int64", "float32", "int32"]
        ]
        return df[cols]

    def imaging_data_drift(
        self,
        reference_csv: Path,
        current_csv: Path,
        output_path: Path,
    ) -> None:
        logger.info("generating imaging data drift report")
        reference = self._drop_non_numeric_cols(pd.read_csv(reference_csv))
        current = self._drop_non_numeric_cols(pd.read_csv(current_csv))

        report = Report([DataDriftPreset()])
        result = report.run(reference, current)
        result.save_html(str(output_path))
        logger.info(f"imaging data drift report saved: {output_path}")

    def clinical_data_drift(
        self,
        reference_csv: Path,
        current_csv: Path,
        output_path: Path,
    ) -> None:
        logger.info("generating clinical data drift report")
        reference = pd.read_csv(reference_csv)
        current = pd.read_csv(current_csv)

        report = Report([DataDriftPreset()])
        result = report.run(reference, current)
        result.save_html(str(output_path))
        logger.info(f"clinical data drift report saved: {output_path}")

    def imaging_classification_performance(
        self,
        reference_csv: Path,
        current_csv: Path,
        output_path: Path,
    ) -> None:
        logger.info("generating imaging classification performance report")
        reference = pd.read_csv(reference_csv)
        current = pd.read_csv(current_csv)

        report = Report([ClassificationPreset()])
        result = report.run(reference, current)
        result.save_html(str(output_path))
        logger.info(f"imaging classification report saved: {output_path}")

    def clinical_classification_performance(
        self,
        reference_csv: Path,
        current_csv: Path,
        output_path: Path,
    ) -> None:
        logger.info("generating clinical classification performance report")
        reference = pd.read_csv(reference_csv)
        current = pd.read_csv(current_csv)

        report = Report([ClassificationPreset()])
        result = report.run(reference, current)
        result.save_html(str(output_path))
        logger.info(f"clinical classification report saved: {output_path}")

    def domain_shift_report(
        self,
        eyepacs_csv: Path,
        samaya_csv: Path,
        output_path: Path,
    ) -> None:
        logger.info("generating domain shift report: EyePACS vs Samaya")
        eyepacs = self._drop_non_numeric_cols(pd.read_csv(eyepacs_csv))
        samaya = self._drop_non_numeric_cols(pd.read_csv(samaya_csv))

        common_cols = list(set(eyepacs.columns) & set(samaya.columns))
        eyepacs = eyepacs[common_cols]
        samaya = samaya[common_cols]

        report = Report([DataDriftPreset()])
        result = report.run(eyepacs, samaya)
        result.save_html(str(output_path))
        logger.info(f"domain shift report saved: {output_path}")

    def run_all(
        self,
        imaging_train_csv: Path,
        imaging_test_csv: Path,
        imaging_samaya_csv: Path,
        clinical_train_csv: Path,
        clinical_test_csv: Path,
    ) -> None:
        logger.info("=" * 60)
        logger.info("running all evidently reports")
        logger.info("=" * 60)

        self.imaging_data_drift(
            reference_csv=imaging_train_csv,
            current_csv=imaging_test_csv,
            output_path=self.reports_dir / "imaging_drift_report.html",
        )

        self.clinical_data_drift(
            reference_csv=clinical_train_csv,
            current_csv=clinical_test_csv,
            output_path=self.reports_dir / "clinical_drift_report.html",
        )

        if imaging_samaya_csv.exists():
            self.domain_shift_report(
                eyepacs_csv=imaging_test_csv,
                samaya_csv=imaging_samaya_csv,
                output_path=self.reports_dir / "domain_shift_report.html",
            )

        logger.info("all evidently reports generated")
        logger.info("=" * 60)