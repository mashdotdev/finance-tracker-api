from fastapi import FastAPI, Request
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app import Settings, get_settings
from contextlib import asynccontextmanager

settings: Settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Database pooling started")
    engine = create_async_engine(
        url=settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        connect_args={"statement_cache_size": 0},
    )
    app.state.async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    print("Database pooling created")

    yield

    await engine.dispose()
    print("Database closed")


async def get_session(request: Request):
    async with request.app.state.async_session() as session:
        yield session
