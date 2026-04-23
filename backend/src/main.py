import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from src.api import router as main_router
from src.config import settings
from src.db import engine, sessionmaker
from src.models.enums import JwtTokenType, UserRole
from src.models.system import AppOption
from src.services.system import APP_UNAVAILABLE_OPTION_CODE
from src.utils.bootstrap import ensure_superuser
from src.utils.db_tools import DBHealthChecker
from src.utils.files import ensure_upload_directory
from src.utils.logging import configurate_logging, get_logger
from src.utils.security import decode_jwt_token


def _normalize_path(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path[:-1]
    return path


def _get_maintenance_exempt_paths() -> set[str]:
    api_base = f"{settings.app.api_prefix}{settings.app.v1_prefix}"
    paths = {
        "/health",
        f"{api_base}/maintenance",
        f"{api_base}/auth/login",
        f"{api_base}/auth/refresh",
        f"{api_base}/auth/logout",
    }

    if settings.app.docs_url:
        paths.add(settings.app.docs_url)
    if settings.app.redoc_url:
        paths.add(settings.app.redoc_url)
    if settings.app.openapi_url:
        paths.add(settings.app.openapi_url)

    return {_normalize_path(path) for path in paths}


MAINTENANCE_EXEMPT_PATHS = _get_maintenance_exempt_paths()


def _has_admin_access(request: Request) -> bool:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return False

    try:
        payload = decode_jwt_token(token, JwtTokenType.ACCESS)
    except HTTPException:
        return False

    return payload.get("role") in {UserRole.ADMIN.value, UserRole.SUPERUSER.value}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    logger = get_logger("src")
    ensure_upload_directory()
    await DBHealthChecker(engine=engine).check()
    await ensure_superuser()
    logger.info("All startup checks passed")
    yield
    logger.info("Application shutdown")


configurate_logging()

app = FastAPI(
    title=settings.app.title,
    lifespan=lifespan,
    docs_url=settings.app.docs_url,
    redoc_url=settings.app.redoc_url,
    openapi_url=settings.app.openapi_url,
)
app.state.db_sessionmaker = sessionmaker

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)


@app.middleware("http")
async def enforce_maintenance_mode(request: Request, call_next):
    normalized_path = _normalize_path(request.url.path)

    if request.method == "OPTIONS" or normalized_path in MAINTENANCE_EXEMPT_PATHS:
        return await call_next(request)

    async with request.app.state.db_sessionmaker() as session:
        maintenance_enabled = await session.scalar(
            select(AppOption.value).where(AppOption.code == APP_UNAVAILABLE_OPTION_CODE)
        )

    is_enabled = str(maintenance_enabled or "").strip().lower() in {"1", "true", "yes", "on"}

    if not is_enabled or _has_admin_access(request):
        return await call_next(request)

    return JSONResponse(
        status_code=503,
        content={
            "detail": "Service is temporarily unavailable due to maintenance",
            "maintenance_enabled": True,
        },
    )


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        reload=settings.uvicorn.reload,
    )
