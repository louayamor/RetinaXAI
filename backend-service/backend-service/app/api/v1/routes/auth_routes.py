import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.exceptions import UnauthorizedException
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from app.auth.session_service import AuthSessionService
from app.db.session import get_db
from app.schemas.token_schema import TokenResponse
from app.schemas.user_schema import UserCreate, UserRead
from app.users.service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = UserService(db)
    return await service.create(data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = UserService(db)
    user = await service.authenticate(form_data.username, form_data.password)
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    session_service = AuthSessionService(db)
    await session_service.create_session(user.id, refresh_token, expires_in_days=7)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    payload = decode_token(data.refresh_token)
    if payload.token_type != "refresh":
        raise UnauthorizedException("Invalid refresh token.")

    session_service = AuthSessionService(db)
    if not await session_service.is_active(data.refresh_token):
        raise UnauthorizedException("Refresh token revoked or expired.")

    user_service = UserService(db)
    user = await user_service.get_by_id(uuid.UUID(payload.sub))
    access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)
    await session_service.rotate_refresh_token(data.refresh_token, new_refresh_token, expires_in_days=7)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    session_service = AuthSessionService(db)
    await session_service.revoke_refresh_token(data.refresh_token)
    return {"status": "ok"}
