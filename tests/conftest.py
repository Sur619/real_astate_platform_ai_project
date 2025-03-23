import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from configs.db import Base

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/testdb"

@pytest.fixture
async def db_session():
    # Создаем асинхронный движок для базы данных
    engine = create_async_engine(DATABASE_URL, echo=True)

    # Создаем sessionmaker с AsyncSession
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Создаем все таблицы для тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаем сессию для тестов
    session = async_session()
    yield session  # Возвращаем сессию для использования в тестах

    # Закрываем сессию
    await session.close()

    # Очищаем базу данных после тестов (удаляем все таблицы)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)