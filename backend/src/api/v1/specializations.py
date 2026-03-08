from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from src.api.v1.dependencies.auth import require_roles
from src.api.v1.dependencies.db import DBSessionDep
from src.models.auth import User
from src.models.doctor import Specialization
from src.models.enums import UserRole
from src.schemas.doctor import SpecializationCreateDTO, SpecializationDTO, SpecializationUpdateDTO

router = APIRouter(prefix="/specializations", tags=["Specializations"])

AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.SUPERUSER))]


@router.get("/", response_model=list[SpecializationDTO])
async def list_specializations(db: DBSessionDep) -> list[SpecializationDTO]:
    result = await db.execute(select(Specialization).order_by(Specialization.name.asc()))
    return [SpecializationDTO.model_validate(item) for item in result.scalars().all()]


@router.post("/", response_model=SpecializationDTO, status_code=status.HTTP_201_CREATED)
async def create_specialization(payload: SpecializationCreateDTO, db: DBSessionDep, _: AdminDep) -> SpecializationDTO:
    exists = await db.scalar(select(Specialization).where(func.lower(Specialization.name) == payload.name.lower()))
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Specialization already exists")

    specialization = Specialization(name=payload.name)
    db.add(specialization)
    await db.commit()
    await db.refresh(specialization)

    return SpecializationDTO.model_validate(specialization)


@router.patch("/{specialization_id}", response_model=SpecializationDTO)
async def update_specialization(
    specialization_id: int,
    payload: SpecializationUpdateDTO,
    db: DBSessionDep,
    _: AdminDep,
) -> SpecializationDTO:
    specialization = await db.scalar(select(Specialization).where(Specialization.id == specialization_id))
    if specialization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found")

    exists = await db.scalar(
        select(Specialization).where(
            func.lower(Specialization.name) == payload.name.lower(),
            Specialization.id != specialization_id,
        )
    )
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Specialization already exists")

    specialization.name = payload.name
    await db.commit()
    return SpecializationDTO.model_validate(specialization)


@router.delete("/{specialization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specialization(specialization_id: int, db: DBSessionDep, _: AdminDep) -> None:
    specialization = await db.scalar(select(Specialization).where(Specialization.id == specialization_id))
    if specialization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found")

    await db.delete(specialization)
    await db.commit()
