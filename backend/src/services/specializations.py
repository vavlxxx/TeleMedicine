from fastapi import HTTPException, status

from src.models.doctor import Specialization
from src.schemas.doctor import SpecializationCreateDTO, SpecializationDTO, SpecializationUpdateDTO
from src.services.base import BaseService


class SpecializationService(BaseService):
    async def list_specializations(self) -> list[SpecializationDTO]:
        specializations = await self.db.specializations.list_all()
        return [SpecializationDTO.model_validate(item) for item in specializations]

    async def create_specialization(self, payload: SpecializationCreateDTO) -> SpecializationDTO:
        exists = await self.db.specializations.find_by_name(payload.name)
        if exists is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Specialization already exists")

        specialization = Specialization(name=payload.name)
        self.db.specializations.add(specialization)
        await self.db.commit()
        await self.db.refresh(specialization)
        return SpecializationDTO.model_validate(specialization)

    async def update_specialization(
        self, specialization_id: int, payload: SpecializationUpdateDTO
    ) -> SpecializationDTO:
        specialization = await self.db.specializations.get_by_id(specialization_id)
        if specialization is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found")

        exists = await self.db.specializations.find_by_name_excluding_id(payload.name, specialization_id)
        if exists is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Specialization already exists")

        specialization.name = payload.name
        await self.db.commit()
        return SpecializationDTO.model_validate(specialization)

    async def delete_specialization(self, specialization_id: int) -> None:
        specialization = await self.db.specializations.get_by_id(specialization_id)
        if specialization is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specialization not found")

        await self.db.delete(specialization)
        await self.db.commit()
