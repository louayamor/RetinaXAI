import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.patient_schema import PatientCreate, PatientRead, PatientUpdate
from app.patients.service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("/", response_model=PatientRead, status_code=201)
async def create_patient(
    data: PatientCreate,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = PatientService(db)
    return await service.create(data)


@router.get("/", response_model=dict)
async def list_patients(
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    service = PatientService(db)
    skip = (page - 1) * size
    patients, total = await service.get_all(skip=skip, limit=size)
    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
        "items": [PatientRead.model_validate(p) for p in patients],
    }


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(
    patient_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = PatientService(db)
    return await service.get_by_id(patient_id)


@router.patch("/{patient_id}", response_model=PatientRead)
async def update_patient(
    patient_id: uuid.UUID,
    data: PatientUpdate,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = PatientService(db)
    return await service.update(patient_id, data)


@router.delete("/{patient_id}", response_model=MessageResponse)
async def delete_patient(
    patient_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = PatientService(db)
    await service.delete(patient_id)
    return MessageResponse(message="Patient deleted successfully.")