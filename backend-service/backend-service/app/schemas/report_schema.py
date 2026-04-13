import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.report import ReportStatus
from app.schemas.common import BaseResponse


class ReportGenerateRequest(BaseModel):
    prediction_id: uuid.UUID


class ReportRead(BaseResponse):
    id: uuid.UUID
    patient_id: uuid.UUID
    prediction_id: uuid.UUID
    generated_by: uuid.UUID
    llm_model: str
    content: str | None
    summary: str | None
    status: ReportStatus
    error_message: str | None
    created_at: datetime
