from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    x_api_key: str | None = Security(api_key_header),
) -> None:
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-API-Key is required")
    if x_api_key != settings.api.api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid API key")
