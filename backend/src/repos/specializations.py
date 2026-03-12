from sqlalchemy import func, select

from src.models.doctor import Specialization
from src.repos.base import BaseRepo


class SpecializationRepo(BaseRepo):
    def add(self, specialization: Specialization) -> None:
        self.session.add(specialization)

    async def list_all(self) -> list[Specialization]:
        statement = select(Specialization).order_by(Specialization.name.asc())
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_by_id(self, specialization_id: int) -> Specialization | None:
        statement = select(Specialization).where(Specialization.id == specialization_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_ids(self, specialization_ids: list[int]) -> list[Specialization]:
        if not specialization_ids:
            return []

        statement = select(Specialization).where(Specialization.id.in_(specialization_ids))
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def find_by_name(self, name: str) -> Specialization | None:
        statement = select(Specialization).where(func.lower(Specialization.name) == name.lower())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def find_by_name_excluding_id(self, name: str, specialization_id: int) -> Specialization | None:
        statement = select(Specialization).where(
            func.lower(Specialization.name) == name.lower(),
            Specialization.id != specialization_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
