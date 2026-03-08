from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.api.v1.dependencies.auth import CurrentUserDep, require_roles, require_verified_doctor
from src.api.v1.dependencies.db import DBSessionDep
from src.api.v1.serializers import to_question
from src.models.auth import User
from src.models.enums import UserRole
from src.models.qa import Question, QuestionComment
from src.schemas.qa import QuestionCommentCreateDTO, QuestionCreateDTO, QuestionDTO

router = APIRouter(prefix="/questions", tags=["Q&A"])

PatientDep = Annotated[User, Depends(require_roles(UserRole.PATIENT))]
VerifiedDoctorDep = Annotated[User, Depends(require_verified_doctor)]


@router.get("/", response_model=list[QuestionDTO])
async def list_questions(
    db: DBSessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[QuestionDTO]:
    result = await db.execute(
        select(Question)
        .options(
            selectinload(Question.author),
            selectinload(Question.comments).selectinload(QuestionComment.author),
        )
        .order_by(Question.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    questions = result.scalars().all()
    return [to_question(item) for item in questions]


@router.get("/{question_id}", response_model=QuestionDTO)
async def get_question(question_id: int, db: DBSessionDep) -> QuestionDTO:
    result = await db.execute(
        select(Question)
        .where(Question.id == question_id)
        .options(
            selectinload(Question.author),
            selectinload(Question.comments).selectinload(QuestionComment.author),
        )
    )
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    return to_question(question)


@router.post("/", response_model=QuestionDTO, status_code=status.HTTP_201_CREATED)
async def create_question(payload: QuestionCreateDTO, db: DBSessionDep, patient: PatientDep) -> QuestionDTO:
    question = Question(text=payload.text.strip(), author_id=patient.id)
    db.add(question)
    await db.commit()

    result = await db.execute(
        select(Question)
        .where(Question.id == question.id)
        .options(selectinload(Question.author), selectinload(Question.comments).selectinload(QuestionComment.author))
    )
    created_question = result.scalar_one()
    return to_question(created_question)


@router.post("/{question_id}/comments", response_model=QuestionDTO, status_code=status.HTTP_201_CREATED)
async def create_comment(
    question_id: int,
    payload: QuestionCommentCreateDTO,
    db: DBSessionDep,
    doctor: VerifiedDoctorDep,
) -> QuestionDTO:
    question = await db.scalar(select(Question).where(Question.id == question_id))
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    db.add(
        QuestionComment(
            text=payload.text.strip(),
            question_id=question_id,
            author_id=doctor.id,
        )
    )
    await db.commit()

    result = await db.execute(
        select(Question)
        .where(Question.id == question_id)
        .options(
            selectinload(Question.author),
            selectinload(Question.comments).selectinload(QuestionComment.author),
        )
    )
    updated_question = result.scalar_one()
    return to_question(updated_question)
