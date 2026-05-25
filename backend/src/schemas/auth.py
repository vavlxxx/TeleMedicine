import re
from datetime import date
from typing import Any

from pydantic import Field, field_validator, model_validator

from src.models.enums import UserGender, UserRole
from src.schemas.base import BaseDTO

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{4,64}$")
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,128}$")


def normalize_username(username: str) -> str:
    username = username.strip().lower()
    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError("Username must be 4-64 chars and contain only letters, numbers, '.', '_' or '-'.")
    return username


def validate_password(password: str) -> str:
    if not PASSWORD_PATTERN.fullmatch(password):
        raise ValueError("Password must be 10-128 chars and include upper, lower, digit and special character.")
    return password


def normalize_optional_name(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def validate_birth_date(value: date | None) -> date | None:
    if value is None:
        return None
    if value > date.today():
        raise ValueError("birth_date cannot be in the future")
    return value


class LoginRequest(BaseDTO):
    username: str = Field(min_length=4, max_length=64)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username_field(cls, value: str) -> str:
        return normalize_username(value)


class RegisterPatientRequest(BaseDTO):
    username: str = Field(min_length=4, max_length=64)
    password: str = Field(min_length=10, max_length=128)
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    middle_name: str | None = Field(default=None, max_length=120)
    gender: UserGender | None = None
    birth_date: date | None = None
    birth_date_visible_to_doctors: bool = False

    @field_validator("username")
    @classmethod
    def normalize_username_field(cls, value: str) -> str:
        return normalize_username(value)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, value: str) -> str:
        return validate_password(value)

    @field_validator("first_name", "last_name", "middle_name")
    @classmethod
    def normalize_name_fields(cls, value: str | None) -> str | None:
        return normalize_optional_name(value)

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date_field(cls, value: date | None) -> date | None:
        return validate_birth_date(value)


class RegisterDoctorMetaRequest(RegisterPatientRequest):
    specialization_ids: list[int] = Field(min_length=1, max_length=20)

    @field_validator("specialization_ids")
    @classmethod
    def unique_specialization_ids(cls, value: list[int]) -> list[int]:
        unique_ids = list(dict.fromkeys(value))
        if len(unique_ids) != len(value):
            raise ValueError("specialization_ids must contain unique values")
        if any(item <= 0 for item in unique_ids):
            raise ValueError("specialization_ids must contain only positive ids")
        return unique_ids


class ProfileUpdateRequest(BaseDTO):
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    middle_name: str | None = Field(default=None, max_length=120)
    gender: UserGender | None = None
    birth_date: date | None = None
    birth_date_visible_to_doctors: bool | None = None

    @field_validator("first_name", "last_name", "middle_name")
    @classmethod
    def normalize_name_fields(cls, value: str | None) -> str | None:
        return normalize_optional_name(value)

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date_field(cls, value: date | None) -> date | None:
        return validate_birth_date(value)

    @model_validator(mode="before")
    @classmethod
    def ensure_any_field(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        has_any_field = False

        for value in data.values():
            if value is None:
                continue

            if isinstance(value, str):
                if value.strip():
                    has_any_field = True
                    break
                continue

            has_any_field = True
            break

        if not has_any_field:
            raise ValueError("Provide at least one profile field")
        return data


class PasswordChangeRequest(BaseDTO):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_field(cls, value: str) -> str:
        return validate_password(value)


class SpecializationInlineDTO(BaseDTO):
    id: int
    name: str


class UserProfileDTO(BaseDTO):
    id: int
    username: str
    role: UserRole
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    gender: UserGender | None = None
    birth_date: date | None = None
    birth_date_visible_to_doctors: bool = False
    avatar_url: str | None = None
    is_active: bool
    is_verified_doctor: bool
    specializations: list[SpecializationInlineDTO] = Field(default_factory=list)
    qualification_documents_count: int = 0


class AuthTokenResponseDTO(BaseDTO):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileDTO


class MessageResponseDTO(BaseDTO):
    detail: str
