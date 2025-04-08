import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from sqlalchemy.orm import selectinload

from configs.db import get_db
from users.auth import get_current_user
from users.models import User, Group, UserGroup
from users.schema import ShowUser, UserCreate
from users.services import UserService, get_user_service
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
    try:
        users = await service.get()
        print(f"Retrieved users: {users}")
        return users
    except Exception as e:
        import traceback
        error_detail = str(e)
        error_trace = traceback.format_exc()
        print(f"Error in get_users: {error_detail}\n{error_trace}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
        service: UserService = Depends(get_user_service)):
    return await service.create(user)


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
    # Check if current user is admin
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign admin privileges"
        )

    # Get target user
    stmt = select(User).options(selectinload(User.groups)).where(User.user_id == user_id)
    result = await db.execute(stmt)
    user = result.unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Check if user is already admin
    if is_admin(user):
        return {"message": "User is already an admin"}

    # Get admin group
    stmt = select(Group).where(Group.name == "admin")
    result = await db.execute(stmt)
    admin_group = result.scalar_one_or_none()

    if not admin_group:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin group not found in the database"
        )

    # Assign user to admin group
    user_group = UserGroup(user_id=user.user_id, group_id=admin_group.group_id)
    db.add(user_group)
    await db.commit()

    return {"message": f"User {user.name} has been made an admin"}
