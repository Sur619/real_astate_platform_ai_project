from fastapi import APIRouter, Depends
from users.schema import User, UserCreate
from users.services import UserService, get_user_service

user_router = APIRouter()


@user_router.get("/users/", response_model=list[User])
async def get_users(service: UserService = Depends(get_user_service)):
    try:
        users = await service.get()
        print(f"Retrieved users: {users}")
        return users
    except Exception as e:
        import traceback
        error_detail = str(e)
        error_trace = traceback.format_exc()
        print(f"Error in get_users: {error_detail}\n{error_trace}")
        raise


@user_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return await service.get_by_id(user_id)


@user_router.post("/users/", response_model=User)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.create(user)


@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    await service.delete(user_id)
    return {"message": "User deleted successfully"}
