from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.models.oct_report import OCTReport

router = APIRouter(prefix="/oct-stats", tags=["oct_stats"])


@router.get("/stats")
async def get_oct_stats(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Total reports
    total = await db.scalar(select(func.count(OCTReport.id)))

    # DR grade distribution
    grade_result = await db.execute(
        select(OCTReport.dr_grade, func.count(OCTReport.id))
        .where(OCTReport.dr_grade.isnot(None))
        .group_by(OCTReport.dr_grade)
    )
    grade_distribution = {row[0]: row[1] for row in grade_result.all()}

    # Eye distribution
    eye_result = await db.execute(
        select(OCTReport.eye, func.count(OCTReport.id))
        .group_by(OCTReport.eye)
    )
    eye_distribution = {row[0]: row[1] for row in eye_result.all()}

    # Edema stats
    edema_count = await db.scalar(
        select(func.count(OCTReport.id)).where(OCTReport.edema == True)
    )
    no_edema_count = await db.scalar(
        select(func.count(OCTReport.id)).where(OCTReport.edema == False)
    )

    # ERM stats
    erm_result = await db.execute(
        select(OCTReport.erm_status, func.count(OCTReport.id))
        .where(OCTReport.erm_status.isnot(None))
        .group_by(OCTReport.erm_status)
    )
    erm_distribution = {row[0]: row[1] for row in erm_result.all()}

    # Thickness averages
    thickness_avg = await db.execute(
        select(
            func.avg(OCTReport.thickness_center_fovea),
            func.avg(OCTReport.thickness_average_thickness),
            func.avg(OCTReport.thickness_total_volume_mm3),
        )
    )
    thickness_row = thickness_avg.first()
    thickness_averages = {
        "center_fovea": round(float(thickness_row[0]), 2) if thickness_row[0] else None,
        "average_thickness": round(float(thickness_row[1]), 2) if thickness_row[1] else None,
        "total_volume_mm3": round(float(thickness_row[2]), 2) if thickness_row[2] else None,
    }

    # Image quality average
    avg_quality = await db.scalar(
        select(func.avg(OCTReport.image_quality)).where(
            OCTReport.image_quality.isnot(None)
        )
    )

    # Reports per patient
    patient_report_count = await db.execute(
        select(
            OCTReport.patient_id, func.count(OCTReport.id)
        ).group_by(OCTReport.patient_id)
    )
    reports_per_patient = [row[1] for row in patient_report_count.all()]
    avg_reports_per_patient = round(
        sum(reports_per_patient) / len(reports_per_patient), 2
    ) if reports_per_patient else 0

    return {
        "total_reports": total or 0,
        "grade_distribution": grade_distribution,
        "eye_distribution": eye_distribution,
        "edema": {"present": edema_count or 0, "absent": no_edema_count or 0},
        "erm_distribution": erm_distribution,
        "thickness_averages": thickness_averages,
        "avg_image_quality": round(float(avg_quality), 2) if avg_quality else None,
        "avg_reports_per_patient": avg_reports_per_patient,
    }
