import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.db.session import get_db

router = APIRouter(prefix="/metrics", tags=["model_metrics"])

IMAGING_METRICS = Path("artifacts/model/imaging/metrics.json")
CLINICAL_METRICS = Path("artifacts/model/clinical/metrics.json")


def _load_metrics(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


@router.get("/")
async def get_model_metrics(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    imaging_raw = _load_metrics(IMAGING_METRICS)
    clinical_raw = _load_metrics(CLINICAL_METRICS)

    imaging = None
    if imaging_raw and imaging_raw.get("eyepacs_test"):
        t = imaging_raw["eyepacs_test"]
        imaging = {
            "accuracy": t.get("accuracy"),
            "qwk": t.get("quadratic_weighted_kappa"),
            "auc": t.get("roc_auc_macro"),
        }

    clinical = None
    if clinical_raw:
        clinical = {
            "accuracy": clinical_raw.get("test_accuracy"),
            "qwk": clinical_raw.get("test_qwk"),
            "auc": clinical_raw.get("test_auc"),
        }

    return {
        "imaging": imaging,
        "clinical": clinical,
    }
