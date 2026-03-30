import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.main import app
from src.models.auth import User
from src.models.enums import UserRole
from src.utils.security import hash_password


async def _create_user(
    db_session: AsyncSession,
    *,
    username: str,
    password: str,
    role: UserRole,
    is_verified_doctor: bool = False,
) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
        is_verified_doctor=is_verified_doctor,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _login(ac: AsyncClient, username: str, password: str) -> tuple[dict[str, str], dict]:
    response = await ac.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    return {"Authorization": f"Bearer {payload['access_token']}"}, payload


@pytest.mark.asyncio
async def test_refresh_rotation_rejects_old_cookie_and_logout_clears_session(ac: AsyncClient) -> None:
    register = await ac.post(
        "/auth/register/patient",
        json={
            "username": "patient_refresh",
            "password": "StrongPass!123",
        },
    )
    assert register.status_code == 201

    _, login_payload = await _login(ac, "patient_refresh", "StrongPass!123")
    first_refresh_token = ac.cookies.get(settings.auth.refresh_cookie_name)
    assert first_refresh_token
    assert login_payload["user"]["qualification_documents_count"] == 0

    refresh = await ac.post("/auth/refresh")
    assert refresh.status_code == 200
    second_refresh_token = ac.cookies.get(settings.auth.refresh_cookie_name)
    assert second_refresh_token
    assert second_refresh_token != first_refresh_token

    refresh_with_old_cookie = await ac.post(
        "/auth/refresh",
        headers={"Cookie": f"{settings.auth.refresh_cookie_name}={first_refresh_token}"},
    )
    assert refresh_with_old_cookie.status_code == 401

    logout = await ac.post("/auth/logout")
    assert logout.status_code == 204

    refresh_after_logout = await ac.post("/auth/refresh")
    assert refresh_after_logout.status_code == 401


@pytest.mark.asyncio
async def test_refresh_cookie_restores_session_for_new_client_after_reload(ac: AsyncClient) -> None:
    register = await ac.post(
        "/auth/register/patient",
        json={
            "username": "patient_reload",
            "password": "StrongPass!123",
        },
    )
    assert register.status_code == 201

    await _login(ac, "patient_reload", "StrongPass!123")
    refresh_token = ac.cookies.get(settings.auth.refresh_cookie_name)
    assert refresh_token

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as fresh_client:
        refresh = await fresh_client.post(
            "/auth/refresh",
            headers={"Cookie": f"{settings.auth.refresh_cookie_name}={refresh_token}"},
        )
        assert refresh.status_code == 200
        assert refresh.json()["user"]["username"] == "patient_reload"
        assert refresh.json()["access_token"]


@pytest.mark.asyncio
async def test_doctor_registration_validates_document_edge_cases(
    ac: AsyncClient, db_session: AsyncSession, monkeypatch
) -> None:
    admin = await _create_user(
        db_session,
        username="admin_uploads",
        password="AdminDocs!123",
        role=UserRole.ADMIN,
    )
    assert admin.role == UserRole.ADMIN

    admin_headers, _ = await _login(ac, "admin_uploads", "AdminDocs!123")
    specialization = await ac.post("/specializations/", json={"name": "Endocrinology"}, headers=admin_headers)
    assert specialization.status_code == 201
    specialization_id = specialization.json()["id"]

    bad_extension = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_bad_ext",
            "password": "DoctorPass!123",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("malware.exe", b"fake-binary", "application/octet-stream"))],
    )
    assert bad_extension.status_code == 400
    assert "Unsupported file extension" in bad_extension.json()["detail"]

    bad_content_type = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_bad_mime",
            "password": "DoctorPass!123",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("license.pdf", b"%PDF-1.4 fake", "text/plain"))],
    )
    assert bad_content_type.status_code == 400
    assert "Unsupported content type" in bad_content_type.json()["detail"]

    empty_file = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_empty_file",
            "password": "DoctorPass!123",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("license.pdf", b"", "application/pdf"))],
    )
    assert empty_file.status_code == 400
    assert empty_file.json()["detail"] == "Empty files are not allowed"

    monkeypatch.setattr(settings.upload, "max_file_size_mb", 1)
    too_large = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_large_file",
            "password": "DoctorPass!123",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("license.pdf", b"x" * (1024 * 1024 + 1), "application/pdf"))],
    )
    assert too_large.status_code == 413
    assert too_large.json()["detail"] == "File exceeds 1 MB limit"


@pytest.mark.asyncio
async def test_admin_moderation_contract_for_doctor_without_documents(
    ac: AsyncClient, db_session: AsyncSession
) -> None:
    await _create_user(
        db_session,
        username="admin_moderation",
        password="AdminFlow!123",
        role=UserRole.ADMIN,
    )
    doctor = await _create_user(
        db_session,
        username="doctor_without_docs",
        password="DoctorFlow!123",
        role=UserRole.DOCTOR,
    )

    admin_headers, _ = await _login(ac, "admin_moderation", "AdminFlow!123")

    pending = await ac.get("/admin/doctors/pending", headers=admin_headers)
    assert pending.status_code == 200
    assert pending.json()["total"] == 1
    assert pending.json()["items"][0]["id"] == doctor.id
    assert pending.json()["items"][0]["qualification_documents"] == []

    detail = await ac.get(f"/admin/doctors/{doctor.id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["qualification_documents"] == []

    verify_without_documents = await ac.patch(
        f"/admin/doctors/{doctor.id}/verify",
        json={"is_verified": True},
        headers=admin_headers,
    )
    assert verify_without_documents.status_code == 400
    assert "at least one uploaded qualification document" in verify_without_documents.json()["detail"]

    keep_unverified = await ac.patch(
        f"/admin/doctors/{doctor.id}/verify",
        json={"is_verified": False},
        headers=admin_headers,
    )
    assert keep_unverified.status_code == 200
    assert keep_unverified.json()["is_verified_doctor"] is False

    missing_doctor = await ac.get("/admin/doctors/9999", headers=admin_headers)
    assert missing_doctor.status_code == 404


@pytest.mark.asyncio
async def test_directory_profile_and_question_flow_contracts(ac: AsyncClient, db_session: AsyncSession) -> None:
    await _create_user(
        db_session,
        username="admin_directory",
        password="AdminDirectory!123",
        role=UserRole.ADMIN,
    )
    admin_headers, _ = await _login(ac, "admin_directory", "AdminDirectory!123")

    specialization = await ac.post("/specializations/", json={"name": "Integration Cardiology"}, headers=admin_headers)
    assert specialization.status_code == 201
    specialization_id = specialization.json()["id"]

    doctor_register = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_directory",
            "password": "DoctorPass!123",
            "first_name": "Elena",
            "last_name": "Romanova",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("license.pdf", b"%PDF-1.4 doctor-directory", "application/pdf"))],
    )
    assert doctor_register.status_code == 201
    doctor_id = doctor_register.json()["id"]

    verify = await ac.patch(
        f"/admin/doctors/{doctor_id}/verify",
        json={"is_verified": True},
        headers=admin_headers,
    )
    assert verify.status_code == 200

    patient_register = await ac.post(
        "/auth/register/patient",
        json={
            "username": "patient_directory",
            "password": "PatientPass!123",
        },
    )
    assert patient_register.status_code == 201
    patient_headers, _ = await _login(ac, "patient_directory", "PatientPass!123")

    directory = await ac.get(f"/doctors/?specialization_id={specialization_id}")
    assert directory.status_code == 200
    assert len(directory.json()) == 1
    assert directory.json()[0]["id"] == doctor_id

    public_profile = await ac.get(f"/doctors/{doctor_id}")
    assert public_profile.status_code == 200
    assert public_profile.json()["username"] == "doctor_directory"

    create_question_unauthorized = await ac.post("/questions/", json={"text": "Can I post anonymously?"})
    assert create_question_unauthorized.status_code == 401

    create_question = await ac.post(
        "/questions/",
        json={"text": "I have chest pain for two days. What should I do next?"},
        headers=patient_headers,
    )
    assert create_question.status_code == 201
    assert create_question.json()["author"]["username"] == "patient_directory"


@pytest.mark.asyncio
async def test_specialization_crud_and_doctor_profile_contract_fields(
    ac: AsyncClient, db_session: AsyncSession
) -> None:
    await _create_user(
        db_session,
        username="admin_specs",
        password="AdminSpecs!123",
        role=UserRole.ADMIN,
    )

    admin_headers, _ = await _login(ac, "admin_specs", "AdminSpecs!123")

    create_z = await ac.post("/specializations/", json={"name": "Zoology"}, headers=admin_headers)
    create_a = await ac.post("/specializations/", json={"name": "Allergology"}, headers=admin_headers)
    assert create_z.status_code == 201
    assert create_a.status_code == 201

    duplicate = await ac.post("/specializations/", json={"name": "allergology"}, headers=admin_headers)
    assert duplicate.status_code == 409

    list_response = await ac.get("/specializations/")
    assert list_response.status_code == 200
    assert [item["name"] for item in list_response.json()] == ["Allergology", "Zoology"]

    update_missing = await ac.patch("/specializations/9999", json={"name": "Neurology"}, headers=admin_headers)
    assert update_missing.status_code == 404

    doctor_register = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_contract",
            "password": "DoctorPass!123",
            "first_name": "Anna",
            "last_name": "Smirnova",
            "specialization_ids": [str(create_z.json()["id"]), str(create_a.json()["id"])],
        },
        files=[("documents", ("license.pdf", b"%PDF-1.4 contract", "application/pdf"))],
    )
    assert doctor_register.status_code == 201
    doctor_payload = doctor_register.json()
    assert doctor_payload["qualification_documents_count"] == 1
    assert [item["name"] for item in doctor_payload["specializations"]] == ["Allergology", "Zoology"]

    _, login_payload = await _login(ac, "doctor_contract", "DoctorPass!123")
    assert login_payload["user"]["qualification_documents_count"] == 1
    assert [item["name"] for item in login_payload["user"]["specializations"]] == ["Allergology", "Zoology"]
