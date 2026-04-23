from sqlalchemy import select

from src.models.system import AppOption
from src.repos.base import BaseRepo


class AppOptionRepo(BaseRepo):
    async def get_by_code(self, code: str) -> AppOption | None:
        result = await self.session.execute(select(AppOption).where(AppOption.code == code))
        return result.scalar_one_or_none()

    async def get_or_create(self, code: str, default_value: str = "") -> AppOption:
        option = await self.get_by_code(code)
        if option is not None:
            return option

        option = AppOption(code=code, value=default_value)
        self.session.add(option)
        await self.session.flush()
        return option
