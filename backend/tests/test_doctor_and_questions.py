import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import User
from src.models.enums import UserRole
from src.utils.security import hash_password


async def _create_admin(db_session: AsyncSession) -> User:
    admin = User(
        username="admin_001",
        password_hash=hash_password("AdminPass!123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.mark.asyncio
async def test_doctor_verification_and_comment_flow(ac: AsyncClient, db_session: AsyncSession) -> None:
    await _create_admin(db_session)

    admin_login = await ac.post("/auth/login", json={"username": "admin_001", "password": "AdminPass!123"})
    assert admin_login.status_code == 200
    admin_access_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_access_token}"}

    create_spec = await ac.post("/specializations/", json={"name": "Cardiology"}, headers=admin_headers)
    assert create_spec.status_code == 201
    specialization_id = create_spec.json()["id"]

    doctor_register = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_001",
            "password": "DoctorPass!123",
            "first_name": "Dmitry",
            "last_name": "Sokolov",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("certificate.pdf", b"%PDF-1.4 test", "application/pdf"))],
    )
    assert doctor_register.status_code == 201
    doctor_id = doctor_register.json()["id"]
    assert doctor_register.json()["is_verified_doctor"] is False

    patient_register = await ac.post(
        "/auth/register/patient",
        json={"username": "patient_qa", "password": "PatientPass!123"},
    )
    assert patient_register.status_code == 201

    patient_login = await ac.post("/auth/login", json={"username": "patient_qa", "password": "PatientPass!123"})
    assert patient_login.status_code == 200
    patient_headers = {"Authorization": f"Bearer {patient_login.json()['access_token']}"}

    question_create = await ac.post(
        "/questions/", json={"text": "I have chest pain for 3 days. What should I do?"}, headers=patient_headers
    )
    assert question_create.status_code == 201
    question_id = question_create.json()["id"]

    doctor_login = await ac.post("/auth/login", json={"username": "doctor_001", "password": "DoctorPass!123"})
    assert doctor_login.status_code == 200
    doctor_headers = {"Authorization": f"Bearer {doctor_login.json()['access_token']}"}

    comment_before_verify = await ac.post(
        f"/questions/{question_id}/comments",
        json={"text": "Please do ECG and blood tests urgently."},
        headers=doctor_headers,
    )
    assert comment_before_verify.status_code == 403

    verify_doctor = await ac.patch(
        f"/admin/doctors/{doctor_id}/verify",
        json={"is_verified": True},
        headers=admin_headers,
    )
    assert verify_doctor.status_code == 200
    assert verify_doctor.json()["is_verified_doctor"] is True
    assert len(verify_doctor.json()["qualification_documents"]) == 1

    public_profile = await ac.get(f"/doctors/{doctor_id}")
    assert public_profile.status_code == 200
    assert public_profile.json()["is_verified_doctor"] is True
    assert "qualification_documents" not in public_profile.json()

    comment_after_verify = await ac.post(
        f"/questions/{question_id}/comments",
        json={"text": "Please do ECG and blood tests urgently."},
        headers=doctor_headers,
    )
    assert comment_after_verify.status_code == 201
    assert len(comment_after_verify.json()["comments"]) == 1
