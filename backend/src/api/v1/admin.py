from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from src.api.v1.dependencies.auth import require_roles
from src.api.v1.dependencies.db import DBSessionDep
from src.api.v1.serializers import to_admin_answer_item, to_admin_question_item, to_admin_user_item, to_doctor_detail
from src.models.auth import User
from src.models.doctor import DoctorQualificationDocument
from src.models.enums import UserRole
from src.models.qa import Question, QuestionComment
from src.schemas.admin import (
    AdminAnswersResponseDTO,
    AdminDashboardResponseDTO,
    AdminOverviewStatsDTO,
    AdminQuestionsResponseDTO,
    AdminUserListItemDTO,
    AdminUsersResponseDTO,
    PendingDoctorsResponseDTO,
    UpdateUserStatusRequestDTO,
    VerifyDoctorRequestDTO,
)
from src.schemas.doctor import DoctorDetailDTO
from src.utils.files import resolve_document_path

router = APIRouter(prefix="/admin", tags=["Admin"])

AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.SUPERUSER))]


def _apply_user_search(statement, search: str | None):
    if not search:
        return statement

    query = f"%{search.strip()}%"
    return statement.where(
        or_(
            User.username.ilike(query),
            User.first_name.ilike(query),
            User.last_name.ilike(query),
        )
    )


@router.get("/dashboard", response_model=AdminDashboardResponseDTO)
async def get_admin_dashboard(
    db: DBSessionDep,
    _: AdminDep,
    users_limit: int = Query(default=12, ge=1, le=200),
    questions_limit: int = Query(default=12, ge=1, le=200),
    answers_limit: int = Query(default=12, ge=1, le=200),
    pending_limit: int = Query(default=12, ge=1, le=200),
) -> AdminDashboardResponseDTO:
    users_result = await db.execute(
        select(User)
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
            selectinload(User.questions),
            selectinload(User.comments),
        )
        .order_by(User.created_at.desc())
        .limit(users_limit)
    )
    users = users_result.scalars().all()

    questions_result = await db.execute(
        select(Question)
        .options(
            selectinload(Question.author),
            selectinload(Question.comments).selectinload(QuestionComment.author),
        )
        .order_by(Question.created_at.desc())
        .limit(questions_limit)
    )
    questions = questions_result.scalars().all()

    answers_result = await db.execute(
        select(QuestionComment)
        .options(selectinload(QuestionComment.author))
        .order_by(QuestionComment.created_at.desc())
        .limit(answers_limit)
    )
    answers = answers_result.scalars().all()

    pending_doctors_result = await db.execute(
        select(User)
        .where(User.role == UserRole.DOCTOR, User.is_verified_doctor.is_(False))
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
        )
        .order_by(User.created_at.desc())
        .limit(pending_limit)
    )
    pending_doctors = pending_doctors_result.scalars().all()

    total_users = await db.scalar(select(func.count(User.id)))
    total_inactive_users = await db.scalar(select(func.count(User.id)).where(User.is_active.is_(False)))
    total_patients = await db.scalar(select(func.count(User.id)).where(User.role == UserRole.PATIENT))
    total_doctors = await db.scalar(select(func.count(User.id)).where(User.role == UserRole.DOCTOR))
    total_verified_doctors = await db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.DOCTOR, User.is_verified_doctor.is_(True))
    )
    total_pending_doctors = await db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.DOCTOR, User.is_verified_doctor.is_(False))
    )
    total_questions = await db.scalar(select(func.count(Question.id)))
    total_answers = await db.scalar(select(func.count(QuestionComment.id)))

    return AdminDashboardResponseDTO(
        stats=AdminOverviewStatsDTO(
            total_users=total_users or 0,
            total_inactive_users=total_inactive_users or 0,
            total_patients=total_patients or 0,
            total_doctors=total_doctors or 0,
            total_verified_doctors=total_verified_doctors or 0,
            total_pending_doctors=total_pending_doctors or 0,
            total_questions=total_questions or 0,
            total_answers=total_answers or 0,
        ),
        users=[to_admin_user_item(user) for user in users],
        questions=[to_admin_question_item(question) for question in questions],
        recent_answers=[to_admin_answer_item(answer) for answer in answers],
        pending_doctors=[to_doctor_detail(item) for item in pending_doctors],
    )


@router.get("/users", response_model=AdminUsersResponseDTO)
async def list_admin_users(
    db: DBSessionDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    is_verified_doctor: bool | None = Query(default=None),
) -> AdminUsersResponseDTO:
    filters = []
    if role is not None:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active.is_(is_active))
    if is_verified_doctor is not None:
        filters.append(User.is_verified_doctor.is_(is_verified_doctor))

    count_statement = select(func.count(User.id))
    items_statement = select(User).options(
        selectinload(User.specializations),
        selectinload(User.qualification_documents),
        selectinload(User.questions),
        selectinload(User.comments),
    )

    if filters:
        count_statement = count_statement.where(*filters)
        items_statement = items_statement.where(*filters)

    count_statement = _apply_user_search(count_statement, search)
    items_statement = _apply_user_search(items_statement, search)

    total = await db.scalar(count_statement)
    result = await db.execute(
        items_statement.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    return AdminUsersResponseDTO(
        items=[to_admin_user_item(user) for user in users],
        total=total or 0,
    )


@router.patch("/users/{user_id}/status", response_model=AdminUserListItemDTO)
async def update_user_status(
    user_id: int,
    payload: UpdateUserStatusRequestDTO,
    db: DBSessionDep,
    admin: AdminDep,
):
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot change your own activity status")

    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
            selectinload(User.questions),
            selectinload(User.comments),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = payload.is_active
    await db.commit()
    await db.refresh(user)

    return to_admin_user_item(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DBSessionDep, admin: AdminDep) -> Response:
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account")

    user = await db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/questions", response_model=AdminQuestionsResponseDTO)
async def list_admin_questions(
    db: DBSessionDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    answered: bool | None = Query(default=None),
) -> AdminQuestionsResponseDTO:
    count_statement = select(func.count(Question.id))
    items_statement = select(Question).options(
        selectinload(Question.author),
        selectinload(Question.comments).selectinload(QuestionComment.author),
    )

    if search:
        query = f"%{search.strip()}%"
        count_statement = count_statement.where(Question.text.ilike(query))
        items_statement = items_statement.where(Question.text.ilike(query))

    if answered is True:
        count_statement = count_statement.where(Question.comments.any())
        items_statement = items_statement.where(Question.comments.any())
    elif answered is False:
        count_statement = count_statement.where(~Question.comments.any())
        items_statement = items_statement.where(~Question.comments.any())

    total = await db.scalar(count_statement)
    result = await db.execute(
        items_statement.order_by(Question.created_at.desc()).offset(offset).limit(limit)
    )
    questions = result.scalars().all()

    return AdminQuestionsResponseDTO(
        items=[to_admin_question_item(question) for question in questions],
        total=total or 0,
    )


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, db: DBSessionDep, _: AdminDep) -> Response:
    question = await db.scalar(select(Question).where(Question.id == question_id))
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    await db.delete(question)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/answers", response_model=AdminAnswersResponseDTO)
async def list_admin_answers(
    db: DBSessionDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    question_id: int | None = Query(default=None, ge=1),
) -> AdminAnswersResponseDTO:
    count_statement = select(func.count(QuestionComment.id))
    items_statement = select(QuestionComment).options(selectinload(QuestionComment.author))

    if search:
        query = f"%{search.strip()}%"
        count_statement = count_statement.where(QuestionComment.text.ilike(query))
        items_statement = items_statement.where(QuestionComment.text.ilike(query))

    if question_id is not None:
        count_statement = count_statement.where(QuestionComment.question_id == question_id)
        items_statement = items_statement.where(QuestionComment.question_id == question_id)

    total = await db.scalar(count_statement)
    result = await db.execute(
        items_statement.order_by(QuestionComment.created_at.desc()).offset(offset).limit(limit)
    )
    answers = result.scalars().all()

    return AdminAnswersResponseDTO(
        items=[to_admin_answer_item(answer) for answer in answers],
        total=total or 0,
    )


@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(answer_id: int, db: DBSessionDep, _: AdminDep) -> Response:
    answer = await db.scalar(select(QuestionComment).where(QuestionComment.id == answer_id))
    if answer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")

    await db.delete(answer)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/doctors/pending", response_model=PendingDoctorsResponseDTO)
async def get_pending_doctors(
    db: DBSessionDep,
    _: AdminDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=120),
) -> PendingDoctorsResponseDTO:
    count_statement = select(func.count(User.id)).where(
        User.role == UserRole.DOCTOR,
        User.is_verified_doctor.is_(False),
    )
    items_statement = (
        select(User)
        .where(
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(False),
        )
        .options(
            selectinload(User.specializations),
            selectinload(User.qualification_documents),
        )
    )

    count_statement = _apply_user_search(count_statement, search)
    items_statement = _apply_user_search(items_statement, search)

    total = await db.scalar(count_statement)
    result = await db.execute(
        items_statement.order_by(User.created_at.desc()).offset(offset).limit(limit)
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
    await db.refresh(doctor)

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
