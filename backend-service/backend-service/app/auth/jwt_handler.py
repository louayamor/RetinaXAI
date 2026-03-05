import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.schemas.token_schema import TokenPayload, TokenResponse


def _create_token(subject: str, expire_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expire_delta
    payload = {"sub": subject, "exp": int(expire.timestamp())}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_tokens(user_id: uuid.UUID) -> TokenResponse:
    access_token = _create_token(
        str(user_id),
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = _create_token(
        str(user_id),
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)
    except jwt.PyJWTError:
        raise UnauthorizedException()