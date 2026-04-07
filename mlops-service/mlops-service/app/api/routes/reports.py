from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path
from loguru import logger

from app.api.dependencies import get_settings
from app.config.settings import Settings
from monitoring.evidently_report import EvidentlyReportGenerator


router = APIRouter()


class ReportsResponse(BaseModel):
    generated: list[str]
    reports_dir: str


@router.post("/reports", response_model=ReportsResponse)
def generate_reports(settings: Settings = Depends(get_settings)):
    reports_dir = Path(os.environ.get("MONITORING_DIR", "artifacts/monitoring"))

    imaging_train = Path(os.environ.get("IMAGING_TRAIN_CSV", "artifacts/data/processed/imaging/train.csv"))
    imaging_test = Path(os.environ.get("IMAGING_TEST_CSV", "artifacts/data/processed/imaging/test.csv"))
    imaging_samaya = Path(os.environ.get("IMAGING_SAMAYA_CSV", "artifacts/data/processed/imaging/samaya.csv"))
    clinical_train = Path(os.environ.get("CLINICAL_TRAIN_CSV", "artifacts/data/processed/clinical/train.csv"))
    clinical_test = Path(os.environ.get("CLINICAL_TEST_CSV", "artifacts/data/processed/clinical/test.csv"))

    missing = [
        str(p) for p in [imaging_train, imaging_test, clinical_train, clinical_test]
        if not p.exists()
    ]
    if missing:
        raise HTTPException(
            status_code=424,
            detail=f"required CSV files not found: {missing}",
        )

    generator = EvidentlyReportGenerator(reports_dir)
    generated = []

    try:
        generator.imaging_data_drift(imaging_train, imaging_test, reports_dir / "imaging_drift_report.html")
        generated.append("imaging_drift_report.html")
    except Exception as e:
        logger.warning(f"imaging drift report failed: {e}")

    try:
        generator.clinical_data_drift(clinical_train, clinical_test, reports_dir / "clinical_drift_report.html")
        generated.append("clinical_drift_report.html")
    except Exception as e:
        logger.warning(f"clinical drift report failed: {e}")

    if imaging_samaya.exists():
        try:
            generator.domain_shift_report(imaging_test, imaging_samaya, reports_dir / "domain_shift_report.html")
            generated.append("domain_shift_report.html")
        except Exception as e:
            logger.warning(f"domain shift report failed: {e}")

    if not generated:
        raise HTTPException(status_code=500, detail="all reports failed to generate")

    logger.info(f"generated {len(generated)} evidently reports")
    return ReportsResponse(generated=generated, reports_dir=str(reports_dir))


@router.get("/reports", response_model=ReportsResponse)
def list_reports(settings: Settings = Depends(get_settings)):
    reports_dir = Path(os.environ.get("MONITORING_DIR", "artifacts/monitoring"))

    if not reports_dir.exists():
        return ReportsResponse(generated=[], reports_dir=str(reports_dir))

    reports = [f.name for f in reports_dir.glob("*.html")]
    return ReportsResponse(generated=reports, reports_dir=str(reports_dir))
