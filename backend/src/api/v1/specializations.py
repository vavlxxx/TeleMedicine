from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.v1.dependencies.auth import require_roles
from src.api.v1.dependencies.db import DBDep
from src.models.auth import User
from src.models.enums import UserRole
from src.schemas.doctor import SpecializationCreateDTO, SpecializationDTO, SpecializationUpdateDTO
from src.services.specializations import SpecializationService

router = APIRouter(prefix="/specializations", tags=["Specializations"])

AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.SUPERUSER))]


@router.get("/", response_model=list[SpecializationDTO])
async def list_specializations(db: DBDep) -> list[SpecializationDTO]:
    return await SpecializationService(db).list_specializations()


@router.post("/", response_model=SpecializationDTO, status_code=status.HTTP_201_CREATED)
async def create_specialization(payload: SpecializationCreateDTO, db: DBDep, _: AdminDep) -> SpecializationDTO:
    return await SpecializationService(db).create_specialization(payload)


@router.patch("/{specialization_id}", response_model=SpecializationDTO)
async def update_specialization(
    specialization_id: int,
    payload: SpecializationUpdateDTO,
    db: DBDep,
    _: AdminDep,
) -> SpecializationDTO:
    return await SpecializationService(db).update_specialization(specialization_id, payload)


@router.delete("/{specialization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specialization(specialization_id: int, db: DBDep, _: AdminDep) -> None:
    await SpecializationService(db).delete_specialization(specialization_id)
