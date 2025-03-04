from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import SessionLocal
from app.pydantic_models import User, UserCreate
from app.repositories import UserRepository

user_router = APIRouter()

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@user_router.get("/users/", response_model=list[User])
async def get_users(db: AsyncSession = Depends(get_db)):
    repository = UserRepository(db)
    return await repository.get_all_users()

@user_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    repository = UserRepository(db)
    user = await repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.post("/users/", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    repository = UserRepository(db)
    return await repository.create(user)

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    repository = UserRepository(db)
    user = await repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await repository.delete(user_id)
    return {"message": "User deleted successfully"}
