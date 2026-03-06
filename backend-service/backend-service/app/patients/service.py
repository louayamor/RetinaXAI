import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.patient import Patient
from app.patients.repository import PatientRepository
from app.schemas.patient_schema import PatientCreate, PatientUpdate


class PatientService:
    def __init__(self, db: AsyncSession):
        self.repo = PatientRepository(db)

    async def create(self, data: PatientCreate) -> Patient:
        existing = await self.repo.get_by_mrn(data.medical_record_number)
        if existing:
            raise ConflictException(
                f"Patient with MRN '{data.medical_record_number}' already exists."
            )
        patient = Patient(**data.model_dump())
        return await self.repo.create(patient)

    async def get_by_id(self, patient_id: uuid.UUID) -> Patient:
        patient = await self.repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundException("Patient", patient_id)
        return patient

    async def get_all(self, skip: int = 0, limit: int = 20) -> tuple[list[Patient], int]:
        patients = await self.repo.get_all(skip, limit)
        total = await self.repo.count()
        return patients, total

    async def update(self, patient_id: uuid.UUID, data: PatientUpdate) -> Patient:
        patient = await self.get_by_id(patient_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(patient, field, value)
        return await self.repo.update(patient)

    async def delete(self, patient_id: uuid.UUID) -> None:
        patient = await self.get_by_id(patient_id)
        await self.repo.delete(patient)