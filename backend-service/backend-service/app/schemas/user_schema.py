import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.common import BaseResponse


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    is_active: bool | None = None


class UserRead(BaseResponse):
    id: uuid.UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime