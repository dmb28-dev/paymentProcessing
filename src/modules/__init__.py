from fastapi import APIRouter

from src.core.config import settings

payment_router = APIRouter(
    prefix=f"/{settings.app_type.value}/payment/v1/payments",
    tags=["payments"],
)

__all__ = ["payment_router"]
