import pytest
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from main import app
from users.models import User
from users.security import create_refresh_token, get_password_hash

client = TestClient(app)


@pytest.mark.asyncio
async def test_refresh_token_valid(db_session):
    # Створюємо користувача вручну
    user = User(
        user_id=uuid.uuid4(),
        name="Test User",
        email="refresh@example.com",
        password=get_password_hash("password")
    )
    db_session.add(user)
    await db_session.commit()

    # Генеруємо валідний refresh token
    refresh_token = create_refresh_token(data={"sub": user.email})

    # Запит до /api/refresh
    response = client.post("/api/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid():
    response = client.post("/api/refresh", json={"refresh_token": "invalid.token.value"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
