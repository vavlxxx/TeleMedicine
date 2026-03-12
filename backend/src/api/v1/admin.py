from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from src.api.v1.dependencies.auth import require_roles
from src.api.v1.dependencies.db import DBDep
from src.models.auth import User
from src.models.enums import UserRole
from src.schemas.admin import (
    AdminAnswersResponseDTO,
    AdminDashboardResponseDTO,
    AdminQuestionsResponseDTO,
    AdminUserListItemDTO,
    AdminUsersResponseDTO,
    PendingDoctorsResponseDTO,
    UpdateUserStatusRequestDTO,
    VerifyDoctorRequestDTO,
)
from src.schemas.doctor import DoctorDetailDTO
from src.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])

AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.SUPERUSER))]


@router.get("/dashboard", response_model=AdminDashboardResponseDTO)
async def get_admin_dashboard(
    db: DBDep,
    _: AdminDep,
    users_limit: int = Query(default=12, ge=1, le=200),
    questions_limit: int = Query(default=12, ge=1, le=200),
    answers_limit: int = Query(default=12, ge=1, le=200),
    pending_limit: int = Query(default=12, ge=1, le=200),
) -> AdminDashboardResponseDTO:
    return await AdminService(db).get_dashboard(
        users_limit=users_limit,
        questions_limit=questions_limit,
        answers_limit=answers_limit,
        pending_limit=pending_limit,
    )


@router.get("/users", response_model=AdminUsersResponseDTO)
async def list_admin_users(
    db: DBDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    is_verified_doctor: bool | None = Query(default=None),
) -> AdminUsersResponseDTO:
    return await AdminService(db).list_users(
        offset=offset,
        limit=limit,
        search=search,
        role=role,
        is_active=is_active,
        is_verified_doctor=is_verified_doctor,
    )


@router.patch("/users/{user_id}/status", response_model=AdminUserListItemDTO)
async def update_user_status(
    user_id: int,
    payload: UpdateUserStatusRequestDTO,
    db: DBDep,
    admin: AdminDep,
) -> AdminUserListItemDTO:
    return await AdminService(db).update_user_status(user_id=user_id, payload=payload, admin=admin)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: DBDep, admin: AdminDep):
    return await AdminService(db).delete_user(user_id=user_id, admin=admin)


@router.get("/questions", response_model=AdminQuestionsResponseDTO)
async def list_admin_questions(
    db: DBDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    answered: bool | None = Query(default=None),
) -> AdminQuestionsResponseDTO:
    return await AdminService(db).list_questions(
        offset=offset,
        limit=limit,
        search=search,
        answered=answered,
    )


@router.delete("/questions/{question_id}", status_code=204)
async def delete_question(question_id: int, db: DBDep, _: AdminDep):
    return await AdminService(db).delete_question(question_id)


@router.get("/answers", response_model=AdminAnswersResponseDTO)
async def list_admin_answers(
    db: DBDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    question_id: int | None = Query(default=None, ge=1),
) -> AdminAnswersResponseDTO:
    return await AdminService(db).list_answers(
        offset=offset,
        limit=limit,
        search=search,
        question_id=question_id,
    )


@router.delete("/answers/{answer_id}", status_code=204)
async def delete_answer(answer_id: int, db: DBDep, _: AdminDep):
    return await AdminService(db).delete_answer(answer_id)


@router.get("/doctors/pending", response_model=PendingDoctorsResponseDTO)
async def get_pending_doctors(
    db: DBDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=120),
) -> PendingDoctorsResponseDTO:
    return await AdminService(db).get_pending_doctors(offset=offset, limit=limit, search=search)


@router.get("/doctors/{doctor_id}", response_model=DoctorDetailDTO)
async def get_doctor_for_moderation(doctor_id: int, db: DBDep, _: AdminDep) -> DoctorDetailDTO:
    return await AdminService(db).get_doctor_for_moderation(doctor_id)


@router.patch("/doctors/{doctor_id}/verify", response_model=DoctorDetailDTO)
async def verify_doctor(
    doctor_id: int,
    payload: VerifyDoctorRequestDTO,
    db: DBDep,
    _: AdminDep,
) -> DoctorDetailDTO:
    return await AdminService(db).verify_doctor(doctor_id=doctor_id, payload=payload)


@router.get("/documents/{document_id}")
async def download_doctor_document(document_id: int, db: DBDep, _: AdminDep) -> FileResponse:
    document = await AdminService(db).get_document_download(document_id)
    return FileResponse(
        path=document.path,
        media_type=document.media_type,
        filename=document.filename,
    )
