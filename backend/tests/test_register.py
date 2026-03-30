import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_requires_strong_password(ac: AsyncClient) -> None:
    response = await ac.post(
        "/auth/register/patient",
        json={"username": "weakpass", "password": "12345678"},
    )
    assert response.status_code == 422
