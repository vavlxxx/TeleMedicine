import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_with_invalid_credentials(ac: AsyncClient) -> None:
    response = await ac.post("/auth/login", json={"username": "missing_user", "password": "StrongPass!123"})
    assert response.status_code == 401
