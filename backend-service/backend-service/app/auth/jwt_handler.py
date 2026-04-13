import uuid
from datetime import UTC, datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.schemas.token_schema import TokenPayload


def _create_token(subject: str, expire_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(UTC) + expire_delta
    payload = {"sub": subject, "exp": int(expire.timestamp()), "token_type": token_type}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: uuid.UUID) -> str:
    return _create_token(
        str(user_id),
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(user_id: uuid.UUID) -> str:
    return _create_token(
        str(user_id),
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)
    except jwt.PyJWTError:
        raise UnauthorizedException()
