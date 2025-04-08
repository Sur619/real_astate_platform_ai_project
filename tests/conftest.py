import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from configs.db import Base
from main import app
from users.repositories import get_db  # або правильний шлях до get_db

# Налаштування тестової бази (SQLite в пам’яті або твій власний PostgreSQL)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


# Фікстура для створення бази перед тестами
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 👉 Основна фікстура для сесії (ось той db_session, що шукає pytest)
@pytest_asyncio.fixture()
async def db_session():
    async with async_session_maker() as session:
        yield session


# 👉 Переозначення залежності get_db FastAPI
@pytest_asyncio.fixture(autouse=True)
async def override_get_db(db_session):
    async def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()
