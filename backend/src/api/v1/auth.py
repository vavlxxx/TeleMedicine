from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.api.v1.dependencies.auth import CurrentUserDep, RefreshContextDep, get_client_ip
from src.api.v1.dependencies.db import DBSessionDep
from src.api.v1.serializers import to_document_dto, to_user_profile
from src.config import settings
from src.models.auth import RefreshSession, User
from src.models.doctor import DoctorQualificationDocument, Specialization, doctor_specializations
from src.models.enums import JwtTokenType, UserRole
from src.schemas.auth import (
    AuthTokenResponseDTO,
    LoginRequest,
    MessageResponseDTO,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    RegisterDoctorMetaRequest,
    RegisterPatientRequest,
    UserProfileDTO,
)
from src.schemas.doctor import DoctorQualificationDocumentDTO
from src.utils.files import save_doctor_document
from src.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_jwt_token,
    generate_jti,
    hash_password,
    hash_token,
    utc_now,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_refresh_cookie(response: Response, token: str, expires_at: datetime) -> None:
    response.set_cookie(
        key=settings.auth.refresh_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth.cookie_secure,
        samesite=settings.auth.cookie_samesite,
        max_age=int(settings.auth.refresh_ttl_days * 24 * 3600),
        expires=expires_at,
        path=settings.auth.refresh_cookie_path,
        domain=settings.auth.cookie_domain,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth.refresh_cookie_name,
        path=settings.auth.refresh_cookie_path,
        domain=settings.auth.cookie_domain,
    )


def _cleanup_files(file_names: list[str]) -> None:
    for file_name in file_names:
        file_path = settings.upload.directory / file_name
        file_path.unlink(missing_ok=True)


async def _load_user_with_profile(db: DBSessionDep, user_id: int) -> User:
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/register/patient", response_model=UserProfileDTO, status_code=status.HTTP_201_CREATED)
async def register_patient(payload: RegisterPatientRequest, db: DBSessionDep) -> UserProfileDTO:
    existing_user = await db.scalar(select(User).where(User.username == payload.username))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=UserRole.PATIENT,
        is_verified_doctor=False,
    )
    db.add(user)
    await db.commit()

    created_user = await _load_user_with_profile(db, user.id)
    return to_user_profile(created_user)


@router.post("/register/doctor", response_model=UserProfileDTO, status_code=status.HTTP_201_CREATED)
async def register_doctor(
    db: DBSessionDep,
    username: str = Form(...),
    password: str = Form(...),
    first_name: str | None = Form(default=None),
    last_name: str | None = Form(default=None),
    specialization_ids: list[int] = Form(...),
    documents: list[UploadFile] = File(...),
) -> UserProfileDTO:
    try:
        payload = RegisterDoctorMetaRequest(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            specialization_ids=specialization_ids,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc

    if not documents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one qualification file is required")
    if len(documents) > settings.upload.max_files_per_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.upload.max_files_per_request} files per request",
        )

    existing_user = await db.scalar(select(User).where(User.username == payload.username))
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    result = await db.execute(select(Specialization).where(Specialization.id.in_(payload.specialization_ids)))
    specializations = result.scalars().all()
    if len(specializations) != len(payload.specialization_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more specialization ids are invalid")

    saved_file_names: list[str] = []
    try:
        user = User(
            username=payload.username,
            password_hash=hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            role=UserRole.DOCTOR,
            is_verified_doctor=False,
        )
        db.add(user)
        await db.flush()

        await db.execute(
            insert(doctor_specializations),
            [{"doctor_id": user.id, "specialization_id": item.id} for item in specializations],
        )

        for upload in documents:
            file_meta = await save_doctor_document(upload)
            saved_file_names.append(file_meta.stored_file_name)
            db.add(
                DoctorQualificationDocument(
                    doctor_id=user.id,
                    original_file_name=file_meta.original_file_name,
                    stored_file_name=file_meta.stored_file_name,
                    content_type=file_meta.content_type,
                    size_bytes=file_meta.size_bytes,
                    sha256=file_meta.sha256,
                )
            )

        await db.commit()
    except HTTPException:
        await db.rollback()
        _cleanup_files(saved_file_names)
        raise
    except IntegrityError as exc:
        await db.rollback()
        _cleanup_files(saved_file_names)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Could not register doctor") from exc

    created_user = await _load_user_with_profile(db, user.id)
    return to_user_profile(created_user)


@router.post("/login", response_model=AuthTokenResponseDTO)
async def login(payload: LoginRequest, db: DBSessionDep, request: Request, response: Response) -> AuthTokenResponseDTO:
    result = await db.execute(
        select(User)
        .where(User.username == payload.username)
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
        )
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token, access_expires = create_access_token(user.id, user.role)
    refresh_jti = generate_jti()
    refresh_token, refresh_expires = create_refresh_token(user.id, refresh_jti)

    db.add(
        RefreshSession(
            jti=refresh_jti,
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            user_agent=(request.headers.get("user-agent") or "")[:512],
            ip_address=get_client_ip(request),
            expires_at=refresh_expires,
        )
    )
    await db.commit()

    _set_refresh_cookie(response, refresh_token, refresh_expires)

    return AuthTokenResponseDTO(
        access_token=access_token,
        expires_in=max(int((access_expires - datetime.now(UTC)).total_seconds()), 1),
        user=to_user_profile(user),
    )


@router.post("/refresh", response_model=AuthTokenResponseDTO)
async def refresh_tokens(
    db: DBSessionDep,
    response: Response,
    request: Request,
    refresh_context: RefreshContextDep,
) -> AuthTokenResponseDTO:
    current_session = refresh_context.refresh_session
    current_session.revoked_at = utc_now()

    access_token, access_expires = create_access_token(refresh_context.user.id, refresh_context.user.role)
    refresh_jti = generate_jti()
    refresh_token, refresh_expires = create_refresh_token(refresh_context.user.id, refresh_jti)

    db.add(
        RefreshSession(
            jti=refresh_jti,
            user_id=refresh_context.user.id,
            token_hash=hash_token(refresh_token),
            user_agent=(request.headers.get("user-agent") or "")[:512],
            ip_address=get_client_ip(request),
            expires_at=refresh_expires,
        )
    )
    await db.commit()

    _set_refresh_cookie(response, refresh_token, refresh_expires)

    return AuthTokenResponseDTO(
        access_token=access_token,
        expires_in=max(int((access_expires - datetime.now(UTC)).total_seconds()), 1),
        user=to_user_profile(refresh_context.user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def logout(db: DBSessionDep, request: Request) -> Response:
    refresh_token = request.cookies.get(settings.auth.refresh_cookie_name)
    if refresh_token:
        try:
            payload = decode_jwt_token(refresh_token, JwtTokenType.REFRESH)
            jti = payload.get("jti")
            if isinstance(jti, str):
                db_session = await db.scalar(
                    select(RefreshSession).where(
                        RefreshSession.jti == jti,
                        RefreshSession.revoked_at.is_(None),
                    )
                )
                if db_session is not None:
                    db_session.revoked_at = utc_now()
                    await db.commit()
        except HTTPException:
            pass

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(response)
    return response


@router.get("/me", response_model=UserProfileDTO)
async def get_my_profile(current_user: CurrentUserDep) -> UserProfileDTO:
    return to_user_profile(current_user)


@router.patch("/me", response_model=UserProfileDTO)
async def update_my_profile(payload: ProfileUpdateRequest, db: DBSessionDep, current_user: CurrentUserDep) -> UserProfileDTO:
    current_user.first_name = payload.first_name if payload.first_name is not None else current_user.first_name
    current_user.last_name = payload.last_name if payload.last_name is not None else current_user.last_name
    await db.commit()

    user = await _load_user_with_profile(db, current_user.id)
    return to_user_profile(user)


@router.post("/change-password", response_model=MessageResponseDTO)
async def change_password(payload: PasswordChangeRequest, db: DBSessionDep, current_user: CurrentUserDep) -> MessageResponseDTO:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    await db.commit()
    return MessageResponseDTO(detail="Password changed")


@router.get("/me/documents", response_model=list[DoctorQualificationDocumentDTO])
async def get_my_documents(current_user: CurrentUserDep) -> list[DoctorQualificationDocumentDTO]:
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can view qualification documents")
    return [to_document_dto(item) for item in sorted(current_user.qualification_documents, key=lambda doc: doc.created_at, reverse=True)]
