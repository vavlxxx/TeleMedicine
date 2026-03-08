import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_patient_and_duplicate_username(ac: AsyncClient) -> None:
    payload = {
        "username": "patient_001",
        "password": "StrongPass!123",
        "first_name": "Ivan",
        "last_name": "Petrov",
    }

    response = await ac.post("/auth/register/patient", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == payload["username"]
    assert body["role"] == "patient"

    duplicate = await ac.post("/auth/register/patient", json=payload)
    assert duplicate.status_code == 409


@pytest.mark.asyncio
async def test_login_me_refresh_logout_flow(ac: AsyncClient) -> None:
    register_payload = {
        "username": "patient_002",
        "password": "StrongPass!123",
        "first_name": "Alex",
        "last_name": "Ivanov",
    }
    register = await ac.post("/auth/register/patient", json=register_payload)
    assert register.status_code == 201

    login = await ac.post(
        "/auth/login",
        json={
            "username": register_payload["username"],
            "password": register_payload["password"],
        },
    )
    assert login.status_code == 200
    login_body = login.json()
    assert login_body["access_token"]
    assert login_body["token_type"] == "bearer"

    access_token = login_body["access_token"]
    me = await ac.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200
    assert me.json()["username"] == register_payload["username"]

    refresh = await ac.post("/auth/refresh")
    assert refresh.status_code == 200
    refresh_body = refresh.json()
    assert refresh_body["access_token"]

    logout = await ac.post("/auth/logout")
    assert logout.status_code == 204

    refresh_after_logout = await ac.post("/auth/refresh")
    assert refresh_after_logout.status_code == 401
