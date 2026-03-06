import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.mri_scans.service import MRIScanService
from app.schemas.common import MessageResponse
from app.schemas.mri_scan_schema import MRIScanRead

router = APIRouter(tags=["mri_scans"])


@router.post("/patients/{patient_id}/scans", response_model=MRIScanRead, status_code=201)
async def upload_scans(
    patient_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    left_scan: UploadFile = File(...),
    right_scan: UploadFile = File(...),
):
    service = MRIScanService(db)
    return await service.upload(patient_id, left_scan, right_scan)


@router.get("/patients/{patient_id}/scans", response_model=list[MRIScanRead])
async def list_patient_scans(
    patient_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = MRIScanService(db)
    return await service.get_by_patient(patient_id)


@router.delete("/scans/{scan_id}", response_model=MessageResponse)
async def delete_scan(
    scan_id: uuid.UUID,
    _: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = MRIScanService(db)
    await service.delete(scan_id)
    return MessageResponse(message="MRI scan deleted successfully.")