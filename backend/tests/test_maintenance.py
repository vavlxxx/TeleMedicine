from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import User
from src.models.enums import UserRole
from src.utils.security import hash_password


async def _create_user(
    db_session: AsyncSession,
    *,
    username: str,
    password: str,
    role: UserRole,
) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
        is_verified_doctor=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def test_maintenance_mode_blocks_non_admins_and_allows_admin_control(ac, db_session: AsyncSession) -> None:
    await _create_user(
        db_session,
        username="admin_maintenance",
        password="AdminPass!123",
        role=UserRole.ADMIN,
    )
    await _create_user(
        db_session,
        username="patient_maintenance",
        password="PatientPass!123",
        role=UserRole.PATIENT,
    )

    initial_state = await ac.get("/maintenance/")
    assert initial_state.status_code == 200
    assert initial_state.json()["enabled"] is False

    admin_login = await ac.post("/auth/login", json={"username": "admin_maintenance", "password": "AdminPass!123"})
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    patient_login = await ac.post(
        "/auth/login",
        json={"username": "patient_maintenance", "password": "PatientPass!123"},
    )
    assert patient_login.status_code == 200
    patient_headers = {"Authorization": f"Bearer {patient_login.json()['access_token']}"}

    enable = await ac.patch("/maintenance/", json={"enabled": True}, headers=admin_headers)
    assert enable.status_code == 200
    assert enable.json()["enabled"] is True

    patient_login_during_maintenance = await ac.post(
        "/auth/login",
        json={"username": "patient_maintenance", "password": "PatientPass!123"},
    )
    assert patient_login_during_maintenance.status_code == 200

    public_questions = await ac.get("/questions/")
    assert public_questions.status_code == 503
    assert public_questions.json()["maintenance_enabled"] is True

    patient_profile = await ac.get("/auth/me", headers=patient_headers)
    assert patient_profile.status_code == 503

    admin_dashboard = await ac.get("/admin/dashboard", headers=admin_headers)
    assert admin_dashboard.status_code == 200

    patient_toggle = await ac.patch("/maintenance/", json={"enabled": False}, headers=patient_headers)
    assert patient_toggle.status_code == 403

    disable = await ac.patch("/maintenance/", json={"enabled": False}, headers=admin_headers)
    assert disable.status_code == 200
    assert disable.json()["enabled"] is False

    questions_after_disable = await ac.get("/questions/")
    assert questions_after_disable.status_code == 200
