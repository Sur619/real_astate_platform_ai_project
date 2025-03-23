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
    user_data = UserCreate(name="Test User", email="test@example.com", password="password")

    # Создаем пользователя
    created_user = await user_repo.create(user_data)

    # Проверяем, что пользователь создан
    assert created_user is not None
    assert created_user.name == "Test User"
    assert created_user.email == "test@example.com"
    assert created_user.password != "password"  # Пароль должен быть хэширован


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user_id = uuid.uuid4()
    user = User(user_id=user_id, name="Test User", email="test@example.com", password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    # Получаем пользователя по ID
    retrieved_user = await user_repo.get_by_id(user_id)

    # Проверяем, что пользователь найден
    assert retrieved_user is not None
    assert retrieved_user.user_id == user_id
    assert retrieved_user.name == "Test User"
    assert retrieved_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user = User(user_id=uuid.uuid4(), name="Test User", email="test@example.com", password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    # Получаем пользователя по email
    retrieved_user = await user_repo.get_by_email("test@example.com")

    # Проверяем, что пользователь найден
    assert retrieved_user is not None
    assert retrieved_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    user_id = uuid.uuid4()
    user = User(user_id=user_id, name="Test User", email="test@example.com", password=get_password_hash("password"))
    db_session.add(user)
    await db_session.commit()

    # Удаляем пользователя
    result = await user_repo.delete(user_id)
    assert result is True

    # Проверяем, что пользователь удален
    deleted_user = await user_repo.get_by_id(user_id)
    assert deleted_user is None