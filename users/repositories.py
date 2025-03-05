from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from users.models import User
from users.schema import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self):
        query = select(User)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, user_id: int):
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: UserCreate):
        new_user = User(name=user.name, email=user.email, password=user.password)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def delete(self, user_id: int):
        user = await self.get_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
