from functools import lru_cache
from fastapi import HTTPException, Depends
from starlette import status
from users.repositories import UserRepository, get_user_repository
from users.schema import UserCreate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get(self):
        return await self.repo.get()

    async def get_by_id(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def create(self, user: UserCreate):
        return await self.repo.create(user)

    async def delete(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await self.repo.delete(user_id)


@lru_cache
def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo)
