from collections.abc import AsyncIterator
from typing import Any

import pytest_asyncio
from dependency_injector import providers
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application import create_app
from src.core.config import settings
from src.dependency.container import Container
from src.modules.payment.infrastructure.uow import PaymentUow
from src.modules.payment.use_case.create_payment.impl import CreatePaymentUseCase
from src.modules.payment.use_case.get_payment.impl import GetPaymentUseCase
from src.persistance.base import Base
from src.persistance.outbox import entity as _outbox_entity
from src.persistance.payment import entity as _payment_entity

# Совпадает с prefix в src.modules.payment_router
PAYMENTS_API_BASE = f"/{settings.app_type.value}/payment/v1/payments"


@pytest_asyncio.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    _ = (_payment_entity, _outbox_entity)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


def _wired_test_container(session_factory: async_sessionmaker[AsyncSession]) -> Container:
    """httpx ASGITransport не вызывает lifespan — wire() нужно вызвать вручную."""
    container = Container()
    container.create_payment_use_case.override(
        providers.Factory(
            CreatePaymentUseCase,
            uow=providers.Factory(PaymentUow, session_factory=session_factory),
        ),
    )
    container.get_payment_use_case.override(
        providers.Factory(
            GetPaymentUseCase,
            uow=providers.Factory(PaymentUow, session_factory=session_factory),
        ),
    )
    container.wire()
    return container


@pytest_asyncio.fixture
async def app(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[FastAPI]:
    fastapi_app = create_app()
    container = _wired_test_container(session_factory)
    fastapi_app.state.core_container = container
    fastapi_app.container = container
    yield fastapi_app
    container.unwire()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


def payment_payload() -> dict[str, Any]:
    return {
        "amount": "100.00",
        "currency": "USD",
        "description": "Test payment",
        "metadata": {"order_id": "A-1"},
        "webhook_url": "https://example.com/webhook",
    }
