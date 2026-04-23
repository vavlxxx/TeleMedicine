from sqlalchemy import select

from src.config import settings
from src.db import sessionmaker
from src.models.auth import User
from src.models.enums import UserRole
from src.schemas.auth import normalize_optional_name, normalize_username, validate_password
from src.utils.logging import get_logger
from src.utils.security import hash_password

logger = get_logger(__name__)


async def ensure_superuser() -> None:
    username_raw = settings.bootstrap.superuser_username
    password_secret = settings.bootstrap.superuser_password

    if not username_raw or password_secret is None:
        raise Exception("Bootstrap superuser is not configured")

    username = normalize_username(username_raw)
    password = validate_password(password_secret.get_secret_value())

    async with sessionmaker() as session:
        existing = await session.scalar(select(User).where(User.username == username))
        if existing is not None:
            if existing.role != UserRole.SUPERUSER:
                existing.role = UserRole.SUPERUSER
                await session.commit()
                logger.warning("User '%s' was promoted to superuser by bootstrap config", username)
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.SUPERUSER,
            first_name=normalize_optional_name(settings.bootstrap.superuser_first_name),
            last_name=normalize_optional_name(settings.bootstrap.superuser_last_name),
            is_active=True,
            is_verified_doctor=False,
        )
        session.add(user)
        await session.commit()
        logger.warning("Bootstrap superuser '%s' created", username)
