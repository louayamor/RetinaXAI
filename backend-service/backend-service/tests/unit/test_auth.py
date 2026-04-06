import uuid
from unittest.mock import AsyncMock

import pytest

from app.api.v1.routes.auth_routes import RefreshRequest, refresh_token
from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token
from app.auth.session_service import AuthSessionService
from app.core.exceptions import UnauthorizedException


def test_create_access_token_marks_type_access() -> None:
    token = create_access_token(uuid.uuid4())
    payload = decode_token(token)

    assert payload.token_type == "access"


def test_create_refresh_token_marks_type_refresh() -> None:
    token = create_refresh_token(uuid.uuid4())
    payload = decode_token(token)

    assert payload.token_type == "refresh"


@pytest.mark.asyncio
async def test_refresh_rejects_access_token() -> None:
    db_session = AsyncMock()
    token = create_access_token(uuid.uuid4())

    with pytest.raises(UnauthorizedException):
        await refresh_token(RefreshRequest(refresh_token=token), db_session)


@pytest.mark.asyncio
async def test_logout_marks_session_revoked() -> None:
    db_session = AsyncMock()
    session_service = AuthSessionService(db_session)
    refresh = create_refresh_token(uuid.uuid4())

    session = _Session()
    db_session.execute = AsyncMock(return_value=_result(session))
    db_session.flush = AsyncMock()

    await session_service.revoke_refresh_token(refresh)
    assert session.revoked is True


class _result:
    def __init__(self, obj):
        self.obj = obj

    def scalar_one_or_none(self):
        return self.obj


class _Session:
    def __init__(self) -> None:
        from datetime import datetime, timedelta, timezone

        self.revoked = False
        self.user_id = uuid.uuid4()
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=1)
