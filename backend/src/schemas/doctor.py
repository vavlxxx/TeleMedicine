from datetime import datetime

from pydantic import Field, field_validator

from src.models.enums import UserRole
from src.schemas.base import BaseDTO


class SpecializationCreateDTO(BaseDTO):
    name: str = Field(min_length=2, max_length=120)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name cannot be empty")
        return normalized


class SpecializationUpdateDTO(BaseDTO):
    name: str = Field(min_length=2, max_length=120)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name cannot be empty")
        return normalized


class SpecializationDTO(BaseDTO):
    id: int
    name: str


class DoctorQualificationDocumentDTO(BaseDTO):
    id: int
    original_file_name: str
    content_type: str
    size_bytes: int
    created_at: datetime


class DoctorListItemDTO(BaseDTO):
    id: int
    username: str
    role: UserRole
    first_name: str | None
    last_name: str | None
    is_verified_doctor: bool
    specializations: list[SpecializationDTO] = Field(default_factory=list)


class DoctorDetailDTO(DoctorListItemDTO):
    qualification_documents: list[DoctorQualificationDocumentDTO] = Field(default_factory=list)
