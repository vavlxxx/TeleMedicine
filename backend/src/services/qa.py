from fastapi import HTTPException, status

from src.api.v1.serializers import to_question
from src.models.auth import User
from src.models.qa import Question, QuestionComment
from src.repos.loaders import QUESTION_OPTIONS
from src.schemas.qa import QuestionCommentCreateDTO, QuestionCreateDTO, QuestionDTO
from src.services.base import BaseService


class QuestionService(BaseService):
    async def list_questions(self, offset: int, limit: int) -> list[QuestionDTO]:
        questions = await self.db.questions.list_public(offset, limit, *QUESTION_OPTIONS)
        return [to_question(item) for item in questions]

    async def get_question(self, question_id: int) -> QuestionDTO:
        question = await self.db.questions.get_by_id(question_id, *QUESTION_OPTIONS)
        if question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        return to_question(question)

    async def create_question(self, payload: QuestionCreateDTO, patient: User) -> QuestionDTO:
        question = Question(text=payload.text.strip(), author_id=patient.id)
        self.db.questions.add(question)
        await self.db.commit()

        created_question = await self.db.questions.get_by_id(question.id, *QUESTION_OPTIONS)
        if created_question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        return to_question(created_question)

    async def create_comment(self, question_id: int, payload: QuestionCommentCreateDTO, doctor: User) -> QuestionDTO:
        question = await self.db.questions.get_by_id(question_id)
        if question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

        self.db.question_comments.add(
            QuestionComment(
                text=payload.text.strip(),
                question_id=question_id,
                author_id=doctor.id,
            )
        )
        await self.db.commit()

        updated_question = await self.db.questions.get_by_id(question_id, *QUESTION_OPTIONS)
        if updated_question is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        return to_question(updated_question)
