from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import bcrypt
import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError
from jwt.exceptions import ExpiredSignatureError

from src.config import settings
from src.models.enums import JwtTokenType, UserRole


def utc_now() -> datetime:
    return datetime.now(UTC)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_jti() -> str:
    return str(uuid4())


def create_access_token(user_id: int, role: UserRole) -> tuple[str, datetime]:
    now = utc_now()
    expires_at = now + timedelta(minutes=settings.auth.access_ttl_minutes)
    payload = {
        "sub": str(user_id),
        "type": JwtTokenType.ACCESS.value,
        "role": role.value,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": settings.auth.issuer,
        "aud": settings.auth.audience,
    }
    token = jwt.encode(payload, settings.auth.secret_key.get_secret_value(), algorithm=settings.auth.algorithm)
    return token, expires_at


def create_refresh_token(user_id: int, jti: str) -> tuple[str, datetime]:
    now = utc_now()
    expires_at = now + timedelta(days=settings.auth.refresh_ttl_days)
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": JwtTokenType.REFRESH.value,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "iss": settings.auth.issuer,
        "aud": settings.auth.audience,
    }
    token = jwt.encode(payload, settings.auth.secret_key.get_secret_value(), algorithm=settings.auth.algorithm)
    return token, expires_at


def decode_jwt_token(token: str, expected_type: JwtTokenType) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.auth.secret_key.get_secret_value(),
            algorithms=[settings.auth.algorithm],
            audience=settings.auth.audience,
            issuer=settings.auth.issuer,
            options={"require": ["exp", "iat", "sub", "type"]},
        )
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    token_type = payload.get("type")
    if token_type != expected_type.value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload
