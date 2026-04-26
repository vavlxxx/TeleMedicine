from sqlalchemy.orm import selectinload

from src.models.auth import User
from src.models.qa import Question, QuestionComment

USER_PROFILE_OPTIONS = (
    selectinload(User.specializations),
    selectinload(User.qualification_documents),
)

ADMIN_USER_OPTIONS = USER_PROFILE_OPTIONS + (
    selectinload(User.questions),
    selectinload(User.comments),
)

DOCTOR_DIRECTORY_OPTIONS = (
    selectinload(User.specializations),
    selectinload(User.refresh_sessions),
)

DOCTOR_DETAIL_OPTIONS = USER_PROFILE_OPTIONS + (selectinload(User.refresh_sessions),)

QUESTION_OPTIONS = (
    selectinload(Question.author),
    selectinload(Question.comments).selectinload(QuestionComment.author),
)

ANSWER_OPTIONS = (selectinload(QuestionComment.author),)
