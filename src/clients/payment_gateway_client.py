import asyncio
import random

from src.utils.enums import PaymentStatus


async def emulate_payment_gateway() -> PaymentStatus:
    await asyncio.sleep(random.uniform(2, 5))
    return PaymentStatus.SUCCEEDED if random.random() < 0.9 else PaymentStatus.FAILED
