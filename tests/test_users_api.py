import io

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from users.models import User, Group, UserGroup
from users.security import get_password_hash
from users.auth import create_access_token
from main import app


def get_auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_user_api(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/users/", json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "password123"
        })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_users_api_as_admin(db_session):
    # Створюємо адміна
    admin = User(
        user_id=uuid.uuid4(),
        name="Admin",
        email="admin@example.com",
        password=get_password_hash("adminpass"),
        is_active=True
    )
    db_session.add(admin)

    admin_group = Group(name="admin")
    db_session.add(admin_group)
    await db_session.flush()

    db_session.add(UserGroup(user_id=admin.user_id, group_id=admin_group.group_id))
    await db_session.commit()

    token = create_access_token(data={"sub": admin.email})

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/users/", headers=get_auth_headers(token))

    assert response.status_code == 200
    assert any(user["email"] == "admin@example.com" for user in response.json())


@pytest.mark.asyncio
async def test_upload_avatar(client: AsyncClient, db_session):
    # Створюємо користувача
    user = User(
        user_id=uuid.uuid4(),
        name="Avatar User",
        email="avatar@example.com",
        password="hashed-password",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    # Створюємо токен
    token = create_access_token({"sub": user.email})

    # Фейковий PNG файл
    image_bytes = io.BytesIO(b"fake image data")
    files = {"file": ("avatar.png", image_bytes, "image/png")}

    # Запит на завантаження аватарки
    response = await client.post(
        f"/api/users/{user.user_id}/avatar",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )

    assert response.status_code == 200
    assert "avatar_url" in response.json()
    assert response.json()["avatar_url"].startswith("https://")
