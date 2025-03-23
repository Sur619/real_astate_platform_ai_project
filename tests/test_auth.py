import pytest
import uuid
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from users.auth import login_for_access_token, get_current_user
from users.repositories import UserRepository
from users.security import create_access_token, get_password_hash
from users.models import User


@pytest.mark.asyncio
async def test_login_for_access_token(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user = User(user_id=uuid.uuid4(), name="Test User", email="test@example.com", password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    form_data = OAuth2PasswordRequestForm(username="test@example.com", password="password", scope="")
    response = await login_for_access_token(form_data, user_repo)

    assert "access_token" in response
    assert response["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_for_access_token_invalid_credentials(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user = User(user_id=uuid.uuid4(), name="Test User", email="test@example.com", password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    form_data = OAuth2PasswordRequestForm(username="test@example.com", password="wrongpassword", scope="")
    with pytest.raises(HTTPException) as exc_info:
        await login_for_access_token(form_data, user_repo)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user = User(user_id=uuid.uuid4(), name="Test User", email="test@example.com", password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    access_token = create_access_token(data={"sub": user.email})
    current_user = await get_current_user(access_token, user_repo)

    assert current_user is not None
    assert current_user.email == user.email


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", user_repo)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED