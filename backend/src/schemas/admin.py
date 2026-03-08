from pydantic import Field

from src.schemas.base import BaseDTO
from src.schemas.doctor import DoctorDetailDTO


class VerifyDoctorRequestDTO(BaseDTO):
    is_verified: bool = True


class PendingDoctorsResponseDTO(BaseDTO):
    items: list[DoctorDetailDTO] = Field(default_factory=list)
    total: int
