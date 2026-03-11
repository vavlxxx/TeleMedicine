from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from src.api.v1.dependencies.auth import CurrentUserDep
from src.api.v1.dependencies.db import DBSessionDep
from src.api.v1.serializers import to_doctor_list_item, to_document_dto
from src.config import settings
from src.models.auth import User
from src.models.doctor import DoctorQualificationDocument
from src.models.enums import UserRole
from src.schemas.doctor import DoctorListItemDTO, DoctorQualificationDocumentDTO
from src.utils.files import save_doctor_document

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[DoctorListItemDTO])
async def list_doctors(
    db: DBSessionDep,
    specialization_id: int | None = Query(default=None, ge=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[DoctorListItemDTO]:
    query = (
        select(User)
        .where(User.role == UserRole.DOCTOR, User.is_verified_doctor.is_(True))
        .options(selectinload(User.specializations))
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if specialization_id is not None:
        query = query.where(User.specializations.any(id=specialization_id))

    result = await db.execute(query)
    doctors = result.scalars().all()
    return [to_doctor_list_item(item) for item in doctors]


@router.get("/{doctor_id}", response_model=DoctorListItemDTO)
async def get_doctor(doctor_id: int, db: DBSessionDep) -> DoctorListItemDTO:
    result = await db.execute(
        select(User)
        .where(User.id == doctor_id, User.role == UserRole.DOCTOR, User.is_verified_doctor.is_(True))
        .options(selectinload(User.specializations))
    )
    doctor = result.scalar_one_or_none()
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return to_doctor_list_item(doctor)


@router.post("/me/documents", response_model=list[DoctorQualificationDocumentDTO], status_code=status.HTTP_201_CREATED)
async def upload_my_documents(
    db: DBSessionDep,
    current_user: CurrentUserDep,
    documents: list[UploadFile] = File(...),
) -> list[DoctorQualificationDocumentDTO]:
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can upload qualification documents")

    if not documents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")
    if len(documents) > settings.upload.max_files_per_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {settings.upload.max_files_per_request} files per request",
        )

    saved_file_names: list[str] = []
    try:
        for upload in documents:
            file_meta = await save_doctor_document(upload)
            saved_file_names.append(file_meta.stored_file_name)
            db.add(
                DoctorQualificationDocument(
                    doctor_id=current_user.id,
                    original_file_name=file_meta.original_file_name,
                    stored_file_name=file_meta.stored_file_name,
                    content_type=file_meta.content_type,
                    size_bytes=file_meta.size_bytes,
                    sha256=file_meta.sha256,
                )
            )

        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        for file_name in saved_file_names:
            (settings.upload.directory / file_name).unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate document") from exc
    except Exception:
        await db.rollback()
        for file_name in saved_file_names:
            (settings.upload.directory / file_name).unlink(missing_ok=True)
        raise

    result = await db.execute(
        select(DoctorQualificationDocument)
        .where(DoctorQualificationDocument.doctor_id == current_user.id)
        .order_by(DoctorQualificationDocument.created_at.desc())
    )
    return [to_document_dto(item) for item in result.scalars().all()]
