from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import ApplicationSettings


@dataclass(slots=True)
class CoreContainer:
    settings: ApplicationSettings
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]


def build_core_container(*, settings: ApplicationSettings) -> CoreContainer:
    engine = create_async_engine(settings.db.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return CoreContainer(settings=settings, engine=engine, session_factory=session_factory)
