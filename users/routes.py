import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from configs.db import get_db
from users.auth import get_current_user
from users.models import User, Group, UserGroup
from users.schema import ShowUser, UserCreate
from users.services import UserService, get_user_service, get_user_uow
from users.unit_of_work import AbstractUnitOfWork
from users.utils import is_admin

user_router = APIRouter()


@user_router.get("/health")
async def health_check():
    return {"status": 200, "message": "OK"}


@user_router.get("/users/", response_model=list[ShowUser])
async def get_users(
        service: UserService = Depends(get_user_service),
        current_user: ShowUser = Depends(get_current_user)
):
    return await service.get()


@user_router.get("/users/{user_id}", response_model=ShowUser)
async def get_user(
        user_id: uuid.UUID,
        service: UserService = Depends(get_user_service),
        current_user: ShowUser = Depends(get_current_user)
):
    return await service.get_by_id(user_id)


@user_router.post("/users/", response_model=ShowUser)
async def create_user(
        user: UserCreate,
        avatar: UploadFile = File(None),
        service: UserService = Depends(get_user_service),

):
    return await service.create(user, avatar)


@user_router.delete("/users/{user_id}")
async def delete_user(
        user_id: UUID,
        service: UserService = Depends(get_user_service),
        current_user: ShowUser = Depends(get_current_user)
):
    result = await service.delete(user_id)
    return {"message": "User deleted successfully"}


@user_router.post("/users/{user_id}/make-admin")
async def make_user_admin(
        user_id: UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign admin privileges"
        )

    stmt = select(User).options(selectinload(User.groups)).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if is_admin(user):
        return {"message": "User is already an admin"}

    stmt = select(Group).where(Group.name == "admin")
    result = await db.execute(stmt)
    admin_group = result.scalar_one_or_none()

    if not admin_group:
        raise HTTPException(status_code=500, detail="Admin group not found")

    user_group = UserGroup(user_id=user.user_id, group_id=admin_group.group_id)
    db.add(user_group)
    await db.commit()

    return {"message": f"User {user.name} has been made an admin"}


# routes.py

@user_router.post("/users/{user_id}/upload-avatar")
async def upload_avatar(
        user_id: UUID,
        file: UploadFile = File(...),
        uow: AbstractUnitOfWork = Depends(get_user_uow),
        service: UserService = Depends(get_user_service),
        current_user: ShowUser = Depends(get_current_user)
):
    url = await service.upload_avatar(user_id, file, uow)
    return {"avatar_url": url}
