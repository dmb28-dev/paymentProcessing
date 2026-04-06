from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton
from pymfdata.rdb.connection import AsyncSQLAlchemy

from src.core.config import settings


class CoreContainer(DeclarativeContainer):
    db = Singleton(AsyncSQLAlchemy, db_uri=str(settings.db.database_url))
