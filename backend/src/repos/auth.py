from sqlalchemy import func, or_, select

from src.models.auth import RefreshSession, User
from src.models.enums import UserRole
from src.repos.base import BaseRepo


class UserRepo(BaseRepo):
    @staticmethod
    def _apply_search(statement, search: str | None):
        if not search:
            return statement

        query = f"%{search.strip()}%"
        return statement.where(
            or_(
                User.username.ilike(query),
                User.first_name.ilike(query),
                User.last_name.ilike(query),
            )
        )

    async def get_by_id(self, user_id: int, *options) -> User | None:
        statement = select(User).where(User.id == user_id)
        if options:
            statement = statement.options(*options)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str, *options) -> User | None:
        statement = select(User).where(User.username == username)
        if options:
            statement = statement.options(*options)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int, *options) -> list[User]:
        statement = select(User).order_by(User.created_at.desc()).limit(limit)
        if options:
            statement = statement.options(*options)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_public_doctors(self, specialization_id: int | None, offset: int, limit: int, *options) -> list[User]:
        statement = (
            select(User)
            .where(User.role == UserRole.DOCTOR, User.is_verified_doctor.is_(True))
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if specialization_id is not None:
            statement = statement.where(User.specializations.any(id=specialization_id))
        if options:
            statement = statement.options(*options)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_public_doctor_by_id(self, doctor_id: int, *options) -> User | None:
        statement = select(User).where(
            User.id == doctor_id,
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(True),
        )
        if options:
            statement = statement.options(*options)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_doctor_by_id(self, doctor_id: int, *options) -> User | None:
        statement = select(User).where(
            User.id == doctor_id,
            User.role == UserRole.DOCTOR,
        )
        if options:
            statement = statement.options(*options)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_filtered(
        self,
        offset: int,
        limit: int,
        search: str | None,
        role: UserRole | None,
        is_active: bool | None,
        is_verified_doctor: bool | None,
        *options,
    ) -> list[User]:
        statement = select(User)

        if role is not None:
            statement = statement.where(User.role == role)
        if is_active is not None:
            statement = statement.where(User.is_active.is_(is_active))
        if is_verified_doctor is not None:
            statement = statement.where(User.is_verified_doctor.is_(is_verified_doctor))

        statement = self._apply_search(statement, search)
        statement = statement.order_by(User.created_at.desc()).offset(offset).limit(limit)
        if options:
            statement = statement.options(*options)

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        search: str | None,
        role: UserRole | None,
        is_active: bool | None,
        is_verified_doctor: bool | None,
    ) -> int:
        statement = select(func.count(User.id))

        if role is not None:
            statement = statement.where(User.role == role)
        if is_active is not None:
            statement = statement.where(User.is_active.is_(is_active))
        if is_verified_doctor is not None:
            statement = statement.where(User.is_verified_doctor.is_(is_verified_doctor))

        statement = self._apply_search(statement, search)
        return int(await self.session.scalar(statement) or 0)

    async def list_pending(self, offset: int, limit: int, search: str | None, *options) -> list[User]:
        statement = select(User).where(
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(False),
        )
        statement = self._apply_search(statement, search)
        statement = statement.order_by(User.created_at.desc()).offset(offset).limit(limit)
        if options:
            statement = statement.options(*options)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_pending(self, search: str | None) -> int:
        statement = select(func.count(User.id)).where(
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(False),
        )
        statement = self._apply_search(statement, search)
        return int(await self.session.scalar(statement) or 0)

    async def count_all(self) -> int:
        return int(await self.session.scalar(select(func.count(User.id))) or 0)

    async def count_inactive(self) -> int:
        statement = select(func.count(User.id)).where(User.is_active.is_(False))
        return int(await self.session.scalar(statement) or 0)

    async def count_by_role(self, role: UserRole) -> int:
        statement = select(func.count(User.id)).where(User.role == role)
        return int(await self.session.scalar(statement) or 0)

    async def count_verified_doctors(self) -> int:
        statement = select(func.count(User.id)).where(
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(True),
        )
        return int(await self.session.scalar(statement) or 0)

    async def count_pending_doctors(self) -> int:
        statement = select(func.count(User.id)).where(
            User.role == UserRole.DOCTOR,
            User.is_verified_doctor.is_(False),
        )
        return int(await self.session.scalar(statement) or 0)


class RefreshSessionRepo(BaseRepo):
    def add(self, refresh_session: RefreshSession) -> None:
        self.session.add(refresh_session)

    async def get_active_by_jti(self, jti: str) -> RefreshSession | None:
        statement = select(RefreshSession).where(
            RefreshSession.jti == jti,
            RefreshSession.revoked_at.is_(None),
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
