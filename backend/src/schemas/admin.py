from datetime import datetime

from pydantic import Field

from src.models.enums import UserRole
from src.schemas.base import BaseDTO
from src.schemas.qa import UserShortDTO
from src.schemas.doctor import DoctorDetailDTO


class VerifyDoctorRequestDTO(BaseDTO):
    is_verified: bool = True


class PendingDoctorsResponseDTO(BaseDTO):
    items: list[DoctorDetailDTO] = Field(default_factory=list)
    total: int


class AdminOverviewStatsDTO(BaseDTO):
    total_users: int
    total_inactive_users: int
    total_patients: int
    total_doctors: int
    total_verified_doctors: int
    total_pending_doctors: int
    total_questions: int
    total_answers: int


class AdminUserListItemDTO(BaseDTO):
    id: int
    username: str
    role: UserRole
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_verified_doctor: bool
    created_at: datetime
    qualification_documents_count: int = 0
    questions_count: int = 0
    comments_count: int = 0


class AdminAnswerListItemDTO(BaseDTO):
    id: int
    question_id: int
    text: str
    created_at: datetime
    author: UserShortDTO


class AdminQuestionListItemDTO(BaseDTO):
    id: int
    text: str
    created_at: datetime
    author: UserShortDTO
    comments_count: int = 0
    latest_answer_at: datetime | None = None
    latest_answer_author: UserShortDTO | None = None


class AdminDashboardResponseDTO(BaseDTO):
    stats: AdminOverviewStatsDTO
    users: list[AdminUserListItemDTO] = Field(default_factory=list)
    questions: list[AdminQuestionListItemDTO] = Field(default_factory=list)
    recent_answers: list[AdminAnswerListItemDTO] = Field(default_factory=list)
    pending_doctors: list[DoctorDetailDTO] = Field(default_factory=list)


class AdminUsersResponseDTO(BaseDTO):
    items: list[AdminUserListItemDTO] = Field(default_factory=list)
    total: int


class AdminQuestionsResponseDTO(BaseDTO):
    items: list[AdminQuestionListItemDTO] = Field(default_factory=list)
    total: int


class AdminAnswersResponseDTO(BaseDTO):
    items: list[AdminAnswerListItemDTO] = Field(default_factory=list)
    total: int


class UpdateUserStatusRequestDTO(BaseDTO):
    is_active: bool
