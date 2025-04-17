from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from configs.db import get_db
from users.models import User, Group, UserGroup
from users.schema import UserCreate
from users.security import get_password_hash
from sqlalchemy.orm import joinedload, selectinload


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db_session = db

    async def get(self):
        query = select(User).options(selectinload(User.groups))
        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, user_id):
        query = select(User).options(joinedload(User.groups)).where(User.user_id == user_id)
        result = await self.db_session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_by_email(self, email: str):
        query = select(User).options(selectinload(User.groups)).where(User.email == email)
        result = await self.db_session.execute(query)
        return result.unique().scalar_one_or_none()

    async def create(self, user: UserCreate, avatar_url: str = None):
        hashed_password = get_password_hash(user.password)
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            is_active=True,
            avatar_url=avatar_url
        )

        self.db_session.add(new_user)
        await self.db_session.flush()

        # Explicitly refresh the user object to include relationships
        await self.db_session.refresh(new_user, ["groups"])

        customer_group = await self.db_session.execute(select(Group).where(Group.name == "customer"))
        customer_group = customer_group.scalar_one_or_none()

        if customer_group:
            user_group = UserGroup(user_id=new_user.user_id, group_id=customer_group.group_id)
            self.db_session.add(user_group)

        await self.db_session.commit()
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
