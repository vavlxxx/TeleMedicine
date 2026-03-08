import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_profile_requires_auth(ac: AsyncClient) -> None:
    response = await ac.get('/auth/me')
    assert response.status_code == 401
