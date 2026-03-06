import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, report_id: uuid.UUID) -> Report | None:
        return await self.db.get(Report, report_id)

    async def get_by_prediction_id(self, prediction_id: uuid.UUID) -> Report | None:
        result = await self.db.execute(
            select(Report).where(Report.prediction_id == prediction_id)
        )
        return result.scalar_one_or_none()

    async def get_by_patient(
        self, patient_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> list[Report]:
        result = await self.db.execute(
            select(Report)
            .where(Report.patient_id == patient_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_patient(self, patient_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Report)
            .where(Report.patient_id == patient_id)
        )
        return result.scalar_one()

    async def create(self, report: Report) -> Report:
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def update(self, report: Report) -> Report:
        await self.db.flush()
        await self.db.refresh(report)
        return report