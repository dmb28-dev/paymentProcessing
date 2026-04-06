import uvicorn

from src.application import create_app
from src.core.config import settings


def main() -> None:
    uvicorn.run(create_app(), host=settings.server.host, port=settings.server.port)


if __name__ == "__main__":
    main()
