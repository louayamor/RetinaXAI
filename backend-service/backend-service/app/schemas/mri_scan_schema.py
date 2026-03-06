import uuid
from datetime import datetime

from app.schemas.common import BaseResponse


class MRIScanRead(BaseResponse):
    id: uuid.UUID
    patient_id: uuid.UUID
    left_scan_path: str
    right_scan_path: str
    scanned_at: datetime
    created_at: datetime