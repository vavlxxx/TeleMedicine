from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.v1.dependencies.auth import require_roles
from src.api.v1.dependencies.db import DBDep
from src.models.auth import User
from src.models.enums import UserRole
from src.schemas.system import MaintenanceStateDTO, MaintenanceUpdateRequestDTO
from src.services.system import MaintenanceService

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.SUPERUSER))]


@router.get("/", response_model=MaintenanceStateDTO)
async def get_maintenance_state(db: DBDep) -> MaintenanceStateDTO:
    return await MaintenanceService(db).get_state()


@router.patch("/", response_model=MaintenanceStateDTO)
async def update_maintenance_state(
    payload: MaintenanceUpdateRequestDTO,
    db: DBDep,
    _: AdminDep,
) -> MaintenanceStateDTO:
    return await MaintenanceService(db).update_state(enabled=payload.enabled)
