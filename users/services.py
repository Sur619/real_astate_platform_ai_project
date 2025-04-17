from fastapi import Depends, UploadFile
import logging
from users.exceptions import UserNotFoundException, UserAlreadyExistsException
from users.schema import UserCreate
from users.security import verify_password, get_password_hash
from users.unit_of_work import AbstractUnitOfWork, SqlAlchemyUnitOfWork
from configs.db import get_db
from users.utils import upload_avatar_to_s3

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    async def get(self):
        async with self.uow:
            return await self.uow.users.get()

    async def get_by_id(self, user_id):
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)
            return user

    async def create(self, user: UserCreate, avatar_file: UploadFile = None):
        async with self.uow:
            existing_user = await self.uow.users.get_by_email(user.email)
            if existing_user:
                raise UserAlreadyExistsException(user.email)
            user.password = get_password_hash(user.password)
            avatar_url = None
            if avatar_file:
                avatar_url = upload_avatar_to_s3(await avatar_file.read(), avatar_file.filename)
            return await self.uow.users.create(user, avatar_url=avatar_url)

    async def delete(self, user_id):
        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id)
            return await self.uow.users.delete(user_id)


async def authenticate_user(email: str, password: str, uow: AbstractUnitOfWork):
    async with uow:
        user = await uow.users.get_by_email(email)
        if not user or not verify_password(password, user.password):
            return None
        return user


def get_user_uow(session=Depends(get_db)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory=lambda: session)


def get_user_service(uow: AbstractUnitOfWork = Depends(get_user_uow)):
    return UserService(uow)
