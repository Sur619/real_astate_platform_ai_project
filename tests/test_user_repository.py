import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from users.models import User
from users.repositories import UserRepository
from users.schema import UserCreate
from users.security import get_password_hash


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    user_data = UserCreate(name="Test User", email=unique_email, password="password")

    created_user = await user_repo.create(user_data)

    assert created_user.email == unique_email
    assert created_user.name == user_data.name


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user_id = uuid.uuid4()
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    user = User(user_id=user_id, name="Test User", email=unique_email, password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    result = await user_repo.get_by_id(user_id)
    assert result is not None
    assert result.email == unique_email


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    user = User(user_id=uuid.uuid4(), name="Test User", email=unique_email, password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    result = await user_repo.get_by_email(unique_email)
    assert result is not None
    assert result.name == "Test User"


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user_id = uuid.uuid4()
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    user = User(user_id=user_id, name="Test User", email=unique_email, password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    await user_repo.delete(user_id)

    result = await user_repo.get_by_id(user_id)
    assert result is None
