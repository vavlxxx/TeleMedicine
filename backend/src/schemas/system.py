from datetime import datetime

from src.schemas.base import BaseDTO


class MaintenanceStateDTO(BaseDTO):
    enabled: bool
    updated_at: datetime | None = None


class MaintenanceUpdateRequestDTO(BaseDTO):
    enabled: bool
