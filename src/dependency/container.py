from src.core.config import settings
from src.core.containers import CoreContainer, build_core_container


def invoke() -> CoreContainer:
    return build_core_container(settings=settings)
