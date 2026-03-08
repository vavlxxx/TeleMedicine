from src.models.auth import User
from src.models.enums import UserRole


def is_admin_or_superuser(user: User) -> bool:
    return user.role in {UserRole.ADMIN, UserRole.SUPERUSER}
