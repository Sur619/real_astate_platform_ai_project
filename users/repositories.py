import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from configs.db import get_db
from users.models import User
from users.schema import UserCreate
from users.security import get_password_hash


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db_session = db

    async def get(self):
        query = select(User)
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, user_id):
        query = select(User).where(User.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            is_active=True
        )

        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)
        return new_user

    async def delete(self, user_id):
        user = await self.get_by_id(user_id)
        if not user:
            return None
        await self.db_session.delete(user)
        await self.db_session.commit()
        return True


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)
