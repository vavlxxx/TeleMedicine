from datetime import datetime

from pydantic import Field

from src.models.enums import UserRole
from src.schemas.base import BaseDTO


class QuestionCreateDTO(BaseDTO):
    text: str = Field(min_length=10, max_length=4000)


class QuestionCommentCreateDTO(BaseDTO):
    text: str = Field(min_length=2, max_length=2000)


class UserShortDTO(BaseDTO):
    id: int
    username: str
    role: UserRole
    first_name: str | None
    last_name: str | None
    is_verified_doctor: bool


class QuestionCommentDTO(BaseDTO):
    id: int
    text: str
    created_at: datetime
    author: UserShortDTO


class QuestionDTO(BaseDTO):
    id: int
    text: str
    created_at: datetime
    author: UserShortDTO
    comments: list[QuestionCommentDTO] = Field(default_factory=list)
