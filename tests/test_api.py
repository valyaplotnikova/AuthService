import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_auth_flow(async_client: AsyncClient):
    # 1. Регистрация
    user = {
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "Testov",
        "role": "patient",
        "password": "password",
        "confirm_password": "password"
    }
    register_response = await async_client.post("/register", json=user)
    assert register_response.status_code == 200

    # 2. Логин
    login_response = await async_client.post(
        "/login",
        data={
            "username": user["email"],
            "password": user["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Доступ к защищенному эндпоинту
    me_response = await async_client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == user["email"]
