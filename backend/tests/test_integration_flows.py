import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.auth import User
from src.models.enums import UserRole
from src.utils.security import hash_password


async def _create_admin(db_session: AsyncSession) -> User:
    admin = User(
        username="admin_ops",
        password_hash=hash_password("AdminOps!123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.mark.asyncio
async def test_health_profile_update_and_password_change(ac: AsyncClient) -> None:
    health = await ac.get("http://test/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    register = await ac.post(
        "/auth/register/patient",
        json={
            "username": "patient_profile",
            "password": "PatientFlow!123",
            "first_name": "Ivan",
            "last_name": "Sidorov",
        },
    )
    assert register.status_code == 201

    login = await ac.post(
        "/auth/login",
        json={
            "username": "patient_profile",
            "password": "PatientFlow!123",
        },
    )
    assert login.status_code == 200
    access_token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    me = await ac.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["username"] == "patient_profile"

    update_profile = await ac.patch(
        "/auth/me",
        json={"first_name": "Irina", "last_name": "Volkova"},
        headers=headers,
    )
    assert update_profile.status_code == 200
    assert update_profile.json()["first_name"] == "Irina"
    assert update_profile.json()["last_name"] == "Volkova"

    bad_password_change = await ac.post(
        "/auth/change-password",
        json={"current_password": "WrongPass!123", "new_password": "UpdatedPass!123"},
        headers=headers,
    )
    assert bad_password_change.status_code == 400

    password_change = await ac.post(
        "/auth/change-password",
        json={"current_password": "PatientFlow!123", "new_password": "UpdatedPass!123"},
        headers=headers,
    )
    assert password_change.status_code == 200
    assert password_change.json()["detail"] == "Password changed"

    old_login = await ac.post(
        "/auth/login",
        json={
            "username": "patient_profile",
            "password": "PatientFlow!123",
        },
    )
    assert old_login.status_code == 401

    new_login = await ac.post(
        "/auth/login",
        json={
            "username": "patient_profile",
            "password": "UpdatedPass!123",
        },
    )
    assert new_login.status_code == 200


@pytest.mark.asyncio
async def test_doctor_documents_admin_download_and_role_guards(ac: AsyncClient, db_session: AsyncSession) -> None:
    await _create_admin(db_session)

    admin_login = await ac.post("/auth/login", json={"username": "admin_ops", "password": "AdminOps!123"})
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    specialization = await ac.post("/specializations/", json={"name": "Neurology"}, headers=admin_headers)
    assert specialization.status_code == 201
    specialization_id = specialization.json()["id"]

    doctor_register = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "doctor_docs",
            "password": "DoctorDocs!123",
            "first_name": "Olga",
            "last_name": "Medvedeva",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("license.pdf", b"%PDF-1.4 initial", "application/pdf"))],
    )
    assert doctor_register.status_code == 201
    doctor_id = doctor_register.json()["id"]

    patient_register = await ac.post(
        "/auth/register/patient",
        json={"username": "patient_docs", "password": "PatientDocs!123"},
    )
    assert patient_register.status_code == 201

    patient_login = await ac.post("/auth/login", json={"username": "patient_docs", "password": "PatientDocs!123"})
    assert patient_login.status_code == 200
    patient_headers = {"Authorization": f"Bearer {patient_login.json()['access_token']}"}

    patient_documents = await ac.get("/auth/me/documents", headers=patient_headers)
    assert patient_documents.status_code == 403

    patient_admin_pending = await ac.get("/admin/doctors/pending", headers=patient_headers)
    assert patient_admin_pending.status_code == 403

    doctor_login = await ac.post("/auth/login", json={"username": "doctor_docs", "password": "DoctorDocs!123"})
    assert doctor_login.status_code == 200
    doctor_headers = {"Authorization": f"Bearer {doctor_login.json()['access_token']}"}

    doctor_documents = await ac.get("/auth/me/documents", headers=doctor_headers)
    assert doctor_documents.status_code == 200
    assert len(doctor_documents.json()) == 1

    uploaded_documents = await ac.post(
        "/doctors/me/documents",
        files=[("documents", ("diploma.png", b"png-content", "image/png"))],
        headers=doctor_headers,
    )
    assert uploaded_documents.status_code == 201
    assert len(uploaded_documents.json()) == 2

    pending = await ac.get("/admin/doctors/pending", headers=admin_headers)
    assert pending.status_code == 200
    assert pending.json()["total"] == 1
    assert pending.json()["items"][0]["id"] == doctor_id
    assert len(pending.json()["items"][0]["qualification_documents"]) == 2

    doctor_detail = await ac.get(f"/admin/doctors/{doctor_id}", headers=admin_headers)
    assert doctor_detail.status_code == 200
    assert len(doctor_detail.json()["qualification_documents"]) == 2

    first_document_id = doctor_detail.json()["qualification_documents"][0]["id"]
    download = await ac.get(f"/admin/documents/{first_document_id}", headers=admin_headers)
    assert download.status_code == 200
    assert download.headers["content-type"] in {"application/pdf", "image/png"}
    assert download.content

    verify = await ac.patch(
        f"/admin/doctors/{doctor_id}/verify",
        json={"is_verified": True},
        headers=admin_headers,
    )
    assert verify.status_code == 200
    assert verify.json()["is_verified_doctor"] is True

    pending_after_verify = await ac.get("/admin/doctors/pending", headers=admin_headers)
    assert pending_after_verify.status_code == 200
    assert pending_after_verify.json()["total"] == 0


@pytest.mark.asyncio
async def test_admin_dashboard_returns_users_questions_answers_and_pending_items(
    ac: AsyncClient, db_session: AsyncSession
) -> None:
    await _create_admin(db_session)

    admin_login = await ac.post("/auth/login", json={"username": "admin_ops", "password": "AdminOps!123"})
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    specialization = await ac.post("/specializations/", json={"name": "Therapy"}, headers=admin_headers)
    assert specialization.status_code == 201
    specialization_id = specialization.json()["id"]

    doctor_register = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "dashboard_doctor",
            "password": "DoctorDash!123",
            "first_name": "Anna",
            "last_name": "Smirnova",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("license.pdf", b"%PDF-1.4 dashboard", "application/pdf"))],
    )
    assert doctor_register.status_code == 201

    patient_register = await ac.post(
        "/auth/register/patient",
        json={
            "username": "dashboard_patient",
            "password": "PatientDash!123",
            "first_name": "Pavel",
            "last_name": "Ivanov",
        },
    )
    assert patient_register.status_code == 201

    patient_login = await ac.post("/auth/login", json={"username": "dashboard_patient", "password": "PatientDash!123"})
    assert patient_login.status_code == 200
    patient_headers = {"Authorization": f"Bearer {patient_login.json()['access_token']}"}

    question = await ac.post(
        "/questions/", json={"text": "Need help with recurring headaches for 2 weeks."}, headers=patient_headers
    )
    assert question.status_code == 201
    question_id = question.json()["id"]

    doctor_login = await ac.post("/auth/login", json={"username": "dashboard_doctor", "password": "DoctorDash!123"})
    assert doctor_login.status_code == 200
    doctor_headers = {"Authorization": f"Bearer {doctor_login.json()['access_token']}"}

    before_verify_reply = await ac.post(
        f"/questions/{question_id}/comments",
        json={"text": "This should not be allowed before verification."},
        headers=doctor_headers,
    )
    assert before_verify_reply.status_code == 403

    verify = await ac.patch(
        f"/admin/doctors/{doctor_register.json()['id']}/verify",
        json={"is_verified": True},
        headers=admin_headers,
    )
    assert verify.status_code == 200

    answer = await ac.post(
        f"/questions/{question_id}/comments",
        json={"text": "Please consult a neurologist and keep a symptom diary."},
        headers=doctor_headers,
    )
    assert answer.status_code == 201

    pending_doctor_register = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "dashboard_pending",
            "password": "DoctorWait!123",
            "first_name": "Irina",
            "last_name": "Sokolova",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("pending.pdf", b"%PDF-1.4 pending", "application/pdf"))],
    )
    assert pending_doctor_register.status_code == 201

    dashboard = await ac.get("/admin/dashboard", headers=admin_headers)
    assert dashboard.status_code == 200
    body = dashboard.json()

    assert body["stats"]["total_users"] == 4
    assert body["stats"]["total_inactive_users"] == 0
    assert body["stats"]["total_patients"] == 1
    assert body["stats"]["total_doctors"] == 2
    assert body["stats"]["total_verified_doctors"] == 1
    assert body["stats"]["total_pending_doctors"] == 1
    assert body["stats"]["total_questions"] == 1
    assert body["stats"]["total_answers"] == 1

    usernames = {item["username"] for item in body["users"]}
    assert {"admin_ops", "dashboard_patient", "dashboard_doctor", "dashboard_pending"} <= usernames

    assert body["questions"][0]["id"] == question_id
    assert body["questions"][0]["comments_count"] == 1
    assert body["questions"][0]["latest_answer_author"]["username"] == "dashboard_doctor"

    assert body["recent_answers"][0]["question_id"] == question_id
    assert body["recent_answers"][0]["author"]["username"] == "dashboard_doctor"

    assert body["pending_doctors"][0]["username"] == "dashboard_pending"


@pytest.mark.asyncio
async def test_admin_lists_filters_and_moderation_actions(ac: AsyncClient, db_session: AsyncSession) -> None:
    admin = await _create_admin(db_session)

    admin_login = await ac.post("/auth/login", json={"username": "admin_ops", "password": "AdminOps!123"})
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    specialization = await ac.post("/specializations/", json={"name": "Cardiology"}, headers=admin_headers)
    assert specialization.status_code == 201
    specialization_id = specialization.json()["id"]

    doctor_register = await ac.post(
        "/auth/register/doctor",
        data={
            "username": "ops_doctor",
            "password": "DoctorOps!123",
            "first_name": "Elena",
            "last_name": "Karpova",
            "specialization_ids": str(specialization_id),
        },
        files=[("documents", ("ops.pdf", b"%PDF-1.4 ops", "application/pdf"))],
    )
    assert doctor_register.status_code == 201
    doctor_id = doctor_register.json()["id"]

    patient_register = await ac.post(
        "/auth/register/patient",
        json={
            "username": "ops_patient",
            "password": "PatientOps!123",
            "first_name": "Oleg",
            "last_name": "Petrov",
        },
    )
    assert patient_register.status_code == 201
    patient_id = patient_register.json()["id"]

    patient_login = await ac.post("/auth/login", json={"username": "ops_patient", "password": "PatientOps!123"})
    assert patient_login.status_code == 200
    patient_headers = {"Authorization": f"Bearer {patient_login.json()['access_token']}"}

    question = await ac.post("/questions/", json={"text": "Sharp chest pain during exercise."}, headers=patient_headers)
    assert question.status_code == 201
    question_id = question.json()["id"]

    verify_doctor = await ac.patch(
        f"/admin/doctors/{doctor_id}/verify",
        json={"is_verified": True},
        headers=admin_headers,
    )
    assert verify_doctor.status_code == 200

    doctor_login = await ac.post("/auth/login", json={"username": "ops_doctor", "password": "DoctorOps!123"})
    assert doctor_login.status_code == 200
    doctor_headers = {"Authorization": f"Bearer {doctor_login.json()['access_token']}"}

    answer = await ac.post(
        f"/questions/{question_id}/comments",
        json={"text": "Please schedule ECG and consult a cardiologist urgently."},
        headers=doctor_headers,
    )
    assert answer.status_code == 201
    answer_id = answer.json()["id"]

    users = await ac.get("/admin/users?search=ops&role=patient", headers=admin_headers)
    assert users.status_code == 200
    assert users.json()["total"] == 1
    assert users.json()["items"][0]["username"] == "ops_patient"

    block_user = await ac.patch(
        f"/admin/users/{patient_id}/status",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert block_user.status_code == 200
    assert block_user.json()["is_active"] is False

    blocked_users = await ac.get("/admin/users?is_active=false", headers=admin_headers)
    assert blocked_users.status_code == 200
    assert blocked_users.json()["total"] == 1
    assert blocked_users.json()["items"][0]["username"] == "ops_patient"

    self_block = await ac.patch(f"/admin/users/{admin.id}/status", json={"is_active": False}, headers=admin_headers)
    assert self_block.status_code == 400

    answered_questions = await ac.get("/admin/questions?answered=true&search=chest", headers=admin_headers)
    assert answered_questions.status_code == 200
    assert answered_questions.json()["total"] == 1
    assert answered_questions.json()["items"][0]["id"] == question_id

    answers = await ac.get(f"/admin/answers?question_id={question_id}&search=ECG", headers=admin_headers)
    assert answers.status_code == 200
    assert answers.json()["total"] == 1
    assert answers.json()["items"][0]["id"] == answer_id

    delete_answer = await ac.delete(f"/admin/answers/{answer_id}", headers=admin_headers)
    assert delete_answer.status_code == 204

    answers_after_delete = await ac.get(f"/admin/answers?question_id={question_id}", headers=admin_headers)
    assert answers_after_delete.status_code == 200
    assert answers_after_delete.json()["total"] == 0

    delete_question = await ac.delete(f"/admin/questions/{question_id}", headers=admin_headers)
    assert delete_question.status_code == 204

    questions_after_delete = await ac.get("/admin/questions", headers=admin_headers)
    assert questions_after_delete.status_code == 200
    assert questions_after_delete.json()["total"] == 0

    delete_user = await ac.delete(f"/admin/users/{patient_id}", headers=admin_headers)
    assert delete_user.status_code == 204

    users_after_delete = await ac.get("/admin/users?search=ops_patient", headers=admin_headers)
    assert users_after_delete.status_code == 200
    assert users_after_delete.json()["total"] == 0
