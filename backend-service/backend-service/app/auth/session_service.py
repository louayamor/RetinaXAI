import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession
from app.core.exceptions import UnauthorizedException


class AuthSessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: uuid.UUID, refresh_token: str, expires_in_days: int) -> AuthSession:
        session = AuthSession(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_by_refresh_token(self, refresh_token: str) -> AuthSession | None:
        result = await self.db.execute(
            select(AuthSession).where(AuthSession.refresh_token == refresh_token)
        )
        return result.scalar_one_or_none()

    async def is_active(self, refresh_token: str) -> bool:
        session = await self.get_by_refresh_token(refresh_token)
        if not session or session.revoked:
            return False
        return session.expires_at > datetime.now(timezone.utc)

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        session = await self.get_by_refresh_token(refresh_token)
        if session:
            session.revoked = True
            await self.db.flush()

    async def rotate_refresh_token(self, old_refresh_token: str, new_refresh_token: str, expires_in_days: int) -> str:
        session = await self.get_by_refresh_token(old_refresh_token)
        if not session or session.revoked:
            raise UnauthorizedException("Refresh token revoked or expired.")
        session.revoked = True
        await self.create_session(session.user_id, new_refresh_token, expires_in_days)
        return new_refresh_token
