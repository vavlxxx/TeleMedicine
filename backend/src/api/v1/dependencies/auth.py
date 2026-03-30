from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.v1.dependencies.db import DBDep
from src.config import settings
from src.models.auth import RefreshSession, User
from src.models.enums import JwtTokenType, UserRole
from src.repos.loaders import USER_PROFILE_OPTIONS
from src.utils.security import decode_jwt_token, hash_token

bearer_auth = HTTPBearer(auto_error=False)


@dataclass
class RefreshAuthContext:
    user: User
    refresh_session: RefreshSession
    payload: dict
    token: str


def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _get_access_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is required")
    return credentials.credentials


async def _load_user_with_profile(user_id: int, db: DBDep) -> User | None:
    return await db.users.get_by_id(user_id, *USER_PROFILE_OPTIONS)


async def get_current_user(
    db: DBDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_auth)],
) -> User:
    token = _get_access_token(credentials)
    payload = decode_jwt_token(token, JwtTokenType.ACCESS)

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token payload") from exc

    user = await _load_user_with_profile(user_id, db)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or missing")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    async def role_checker(user: CurrentUserDep) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return user

    return role_checker


async def require_verified_doctor(user: Annotated[User, Depends(require_roles(UserRole.DOCTOR))]) -> User:
    if not user.is_verified_doctor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor is not verified")
    return user


async def get_refresh_context(request: Request, db: DBDep) -> RefreshAuthContext:
    refresh_token = request.cookies.get(settings.auth.refresh_cookie_name)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required")

    payload = decode_jwt_token(refresh_token, JwtTokenType.REFRESH)
    jti = payload.get("jti")
    sub = payload.get("sub")
    if not jti or not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")

    refresh_session = await db.refresh_sessions.get_active_by_jti(jti)
    if refresh_session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session not found")

    expires_at = refresh_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh session expired")

    if refresh_session.token_hash != hash_token(refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token mismatch")

    try:
        user_id = int(sub)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id in refresh token"
        ) from exc

    if refresh_session.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh session subject")

    user = await _load_user_with_profile(user_id, db)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or missing")

    return RefreshAuthContext(
        user=user,
        refresh_session=refresh_session,
        payload=payload,
        token=refresh_token,
    )


RefreshContextDep = Annotated[RefreshAuthContext, Depends(get_refresh_context)]
