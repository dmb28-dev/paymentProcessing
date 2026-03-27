from fastapi import APIRouter

payment_router = APIRouter(
    prefix="/api/v1/payments",
    tags=["payments"],
)

__all__ = ["payment_router"]
