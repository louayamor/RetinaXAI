import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction


class PredictionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, prediction_id: uuid.UUID) -> Prediction | None:
        return await self.db.get(Prediction, prediction_id)

    async def get_by_patient(
        self, patient_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> list[Prediction]:
        result = await self.db.execute(
            select(Prediction)
            .where(Prediction.patient_id == patient_id)
            .order_by(Prediction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[Prediction]:
        result = await self.db.execute(
            select(Prediction)
            .order_by(Prediction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_all(self) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Prediction)
        )
        return result.scalar_one()

    async def count_by_patient(self, patient_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Prediction)
            .where(Prediction.patient_id == patient_id)
        )
        return result.scalar_one()

    async def create(self, prediction: Prediction) -> Prediction:
        self.db.add(prediction)
        await self.db.flush()
        await self.db.refresh(prediction)
        return prediction

    async def update(self, prediction: Prediction) -> Prediction:
        await self.db.flush()
        await self.db.refresh(prediction)
        return prediction