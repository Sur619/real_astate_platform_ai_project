from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configs.settings import Settings

settings = Settings()
DATABASE_URL = settings.database_url

metadata = MetaData()
engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()
