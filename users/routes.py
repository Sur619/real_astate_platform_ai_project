from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db import SessionLocal
from users.schema import User, UserCreate
from users.repositories import UserRepository
from users.services import UserService

user_router = APIRouter()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


def get_service(session=Depends(get_db)):
    return UserService(session)


@user_router.get("/users/", response_model=list[User])
async def get_users(service: UserService = Depends(get_service)):
    return await service.get()


@user_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, service: UserService = Depends(get_service)):
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.post("/users/", response_model=User)
async def create_user(user: UserCreate, service: UserService = Depends(get_service)):
    return await service.create(user)


@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, service: UserService = Depends(get_service)):
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await service.delete(user_id)
    return {"message": "User deleted successfully"}
