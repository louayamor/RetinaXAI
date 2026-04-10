from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.models.patient import Patient
from app.models.prediction import Prediction, PredictionStatus
from app.models.report import Report, ReportStatus
from app.models.mri_scan import MRIScan

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get comprehensive dashboard statistics."""

    # Count totals
    total_patients = await db.scalar(select(func.count(Patient.id)))
    total_predictions = await db.scalar(select(func.count(Prediction.id)))
    total_reports = await db.scalar(select(func.count(Report.id)))
    total_scans = await db.scalar(select(func.count(MRIScan.id)))

    # Prediction status distribution
    prediction_status_result = await db.execute(
        select(Prediction.status, func.count(Prediction.id))
        .group_by(Prediction.status)
    )
    prediction_status_counts = {row[0].value: row[1] for row in prediction_status_result.all()}

    # Report status distribution
    report_status_result = await db.execute(
        select(Report.status, func.count(Report.id))
        .group_by(Report.status)
    )
    report_status_counts = {row[0].value: row[1] for row in report_status_result.all()}

    # Predictions by severity (from output_payload)
    severity_result = await db.execute(
        select(Prediction.output_payload)
        .where(Prediction.output_payload.isnot(None))
    )
    severity_counts = {}
    for row in severity_result.all():
        payload = row[0]
        if isinstance(payload, dict):
            # Try to get severity from combined_prediction or imaging_prediction
            combined = payload.get("combined_prediction", {})
            if not combined:
                combined = payload.get("imaging_prediction", {})
            predicted_class = combined.get("predicted_class")
            if predicted_class is not None:
                severity_counts[predicted_class] = severity_counts.get(predicted_class, 0) + 1

    # Predictions over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    predictions_over_time = await db.execute(
        select(Prediction.created_at).where(Prediction.created_at >= thirty_days_ago)
    )
    timeline_map: dict[str, int] = {}
    for (created_at,) in predictions_over_time.all():
        date_key = created_at.date().isoformat()
        timeline_map[date_key] = timeline_map.get(date_key, 0) + 1

    # Fill in missing dates
    date_range = []
    current = thirty_days_ago.date()
    end = datetime.utcnow().date()
    while current <= end:
        date_range.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)

    filled_timeline = [
        {"date": date, "predictions": timeline_map.get(date, 0)}
        for date in date_range
    ]

    # Patients by age groups
    age_group_expr = case(
        (Patient.age < 18, "Under 18"),
        (Patient.age < 30, "18-29"),
        (Patient.age < 50, "30-49"),
        (Patient.age < 65, "50-64"),
        (Patient.age >= 65, "65+"),
        else_="Unknown",
    ).label("age_group")
    age_groups = await db.execute(
        select(
            age_group_expr,
            func.count(Patient.id).label("count"),
        )
        .group_by(age_group_expr)
        .order_by(age_group_expr)
    )
    age_distribution = {row[0]: row[1] for row in age_groups.all()}

    # Gender distribution
    gender_result = await db.execute(
        select(Patient.gender, func.count(Patient.id))
        .group_by(Patient.gender)
    )
    gender_distribution = {row[0].value: row[1] for row in gender_result.all()}

    # Recent activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_predictions = await db.scalar(
        select(func.count(Prediction.id))
        .where(Prediction.created_at >= seven_days_ago)
    )
    recent_reports = await db.scalar(
        select(func.count(Report.id))
        .where(Report.created_at >= seven_days_ago)
    )
    recent_patients = await db.scalar(
        select(func.count(Patient.id))
        .where(Patient.created_at >= seven_days_ago)
    )

    # Average confidence score for successful predictions
    avg_confidence = await db.scalar(
        select(func.avg(Prediction.confidence_score))
        .where(
            Prediction.status == PredictionStatus.SUCCESS,
            Prediction.confidence_score.isnot(None)
        )
    )

    return {
        "totals": {
            "patients": total_patients or 0,
            "predictions": total_predictions or 0,
            "reports": total_reports or 0,
            "scans": total_scans or 0,
        },
        "prediction_status": prediction_status_counts,
        "report_status": report_status_counts,
        "severity_distribution": severity_counts,
        "predictions_timeline": filled_timeline,
        "age_distribution": age_distribution,
        "gender_distribution": gender_distribution,
        "recent_activity": {
            "new_patients": recent_patients or 0,
            "new_predictions": recent_predictions or 0,
            "new_reports": recent_reports or 0,
        },
        "avg_confidence": round(float(avg_confidence), 2) if avg_confidence else None,
    }
