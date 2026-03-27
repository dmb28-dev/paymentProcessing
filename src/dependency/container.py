from src.core.config import get_settings
from src.core.containers import CoreContainer, build_core_container


def invoke() -> CoreContainer:
    return build_core_container(settings=get_settings())
