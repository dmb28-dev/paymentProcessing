from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from src.core.config import settings
from src.core.fastapi.auth import require_api_key
from src.core.fastapi.errors import register_error_handlers
from src.core.fastapi.routes import include_routers
from src.dependency.container import invoke as build_container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = build_container()
    db = container.db()
    await db.connect(pool_pre_ping=True)
    db.init_session_factory()
    container.wire()
    app.container = container
    app.state.core_container = container
    yield
    container.unwire()
    await db.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(
        title="payment-processing-service",
        lifespan=lifespan,
        dependencies=[Depends(require_api_key)],
        docs_url=f"/{settings.app_type.value}/payment/docs",
        openapi_url=f"/{settings.app_type.value}/payment/openapi.json"
    )
    register_error_handlers(app)
    include_routers(app)
    return app

app = create_app()