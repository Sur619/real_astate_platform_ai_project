import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from users.schema import ShowUser, UserCreate
from users.services import UserService, get_user_service
from users.auth import get_current_user

user_router = APIRouter()


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
