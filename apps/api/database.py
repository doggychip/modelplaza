import os
from typing import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase

from config import settings

SERVERLESS = os.environ.get("VERCEL", "") == "1"


class Base(DeclarativeBase):
    pass


if SERVERLESS:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker

    sync_url = settings.database_url
    if sync_url.startswith("postgresql+asyncpg://"):
        sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    engine = create_engine(
        sync_url, echo=False, pool_pre_ping=True, pool_size=1, pool_recycle=300
    )
    _SessionLocal = sessionmaker(engine, class_=Session, expire_on_commit=False)

    class _SyncSessionWrapper:
        """Wraps sync Session. Methods return the result directly.
        FastAPI async routes calling `await db.execute()` will work because
        awaiting a non-coroutine in an async context just returns the value."""

        def __init__(self, session: Session):
            self._s = session

        def add(self, instance):
            self._s.add(instance)

        async def execute(self, *args, **kwargs):
            return self._s.execute(*args, **kwargs)

        async def commit(self):
            self._s.commit()

        async def refresh(self, instance, **kwargs):
            self._s.refresh(instance, **kwargs)

        async def delete(self, instance):
            self._s.delete(instance)

        def close(self):
            self._s.close()

    async def get_db() -> AsyncGenerator:
        session = _SyncSessionWrapper(_SessionLocal())
        try:
            yield session
        finally:
            session.close()

else:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(settings.async_database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def get_db() -> AsyncGenerator:
        async with async_session() as session:
            yield session
