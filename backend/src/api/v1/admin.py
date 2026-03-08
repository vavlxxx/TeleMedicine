from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.v1.dependencies.auth import require_roles
from src.api.v1.dependencies.db import DBSessionDep
from src.api.v1.serializers import to_doctor_detail
from src.models.auth import User
from src.models.doctor import DoctorQualificationDocument
from src.models.enums import UserRole
from src.schemas.admin import PendingDoctorsResponseDTO, VerifyDoctorRequestDTO
from src.schemas.doctor import DoctorDetailDTO
from src.utils.files import resolve_document_path

router = APIRouter(prefix="/admin", tags=["Admin"])

AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.SUPERUSER))]


@router.get("/doctors/pending", response_model=PendingDoctorsResponseDTO)
async def get_pending_doctors(
    db: DBSessionDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PendingDoctorsResponseDTO:
    total = await db.scalar(
        select(func.count(User.id)).where(
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(False),
        )
    )

    result = await db.execute(
        select(User)
        .where(
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(False),
        )
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
        )
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    doctors = result.scalars().all()

    return PendingDoctorsResponseDTO(
        items=[to_doctor_detail(item) for item in doctors],
        total=total or 0,
    )


@router.get("/doctors/{doctor_id}", response_model=DoctorDetailDTO)
async def get_doctor_for_moderation(doctor_id: int, db: DBSessionDep, _: AdminDep) -> DoctorDetailDTO:
    result = await db.execute(
        select(User)
        .where(User.id == doctor_id, User.role == UserRole.DOCTOR)
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
        )
    )
    doctor = result.scalar_one_or_none()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    return to_doctor_detail(doctor)


@router.patch("/doctors/{doctor_id}/verify", response_model=DoctorDetailDTO)
async def verify_doctor(
    doctor_id: int,
    payload: VerifyDoctorRequestDTO,
    db: DBSessionDep,
    _: AdminDep,
) -> DoctorDetailDTO:
    result = await db.execute(
        select(User)
        .where(User.id == doctor_id, User.role == UserRole.DOCTOR)
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
        )
    )
    doctor = result.scalar_one_or_none()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if payload.is_verified and not doctor.qualification_documents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor must have at least one uploaded qualification document",
        )

    doctor.is_verified_doctor = payload.is_verified
    await db.commit()

    return to_doctor_detail(doctor)


@router.get("/documents/{document_id}")
async def download_doctor_document(document_id: int, db: DBSessionDep, _: AdminDep) -> FileResponse:
    document = await db.scalar(select(DoctorQualificationDocument).where(DoctorQualificationDocument.id == document_id))
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    file_path = resolve_document_path(document.stored_file_name)
    return FileResponse(
        path=file_path,
        media_type=document.content_type,
        filename=document.original_file_name,
    )
