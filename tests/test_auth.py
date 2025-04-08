import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from users.repositories import UserRepository
from users.models import User
from users.security import get_password_hash
from users.services import authenticate_user


@pytest.mark.asyncio
async def test_login_for_access_token(db_session: AsyncSession):
    # Створюємо користувача
    user_repo = UserRepository(db_session)
    user = User(
        user_id=uuid.uuid4(),
        name="Test User",
        email="test@example.com",
        password=get_password_hash("password"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    # Перевіряємо логіку автентифікації
    authenticated_user = await authenticate_user(
        email="test@example.com",
        password="password",
        user_repo=user_repo
    )

    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"
