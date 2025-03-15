from functools import lru_cache
from fastapi import HTTPException, Depends
from starlette import status

from users.exceptions import UserNotFoundException, UserAlreadyExistsException
from users.repositories import UserRepository, get_user_repository
from users.schema import UserCreate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get(self):
        return await self.repo.get()

    async def get_by_id(self, user_id):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user

    async def create(self, user: UserCreate):
        existing_user = await self.repo.get_by_email(user.email)
        if existing_user:
            raise UserAlreadyExistsException(user.email)
        return await self.repo.create(user)

    async def delete(self, user_id):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return await self.repo.delete(user_id)


@lru_cache
def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo)
