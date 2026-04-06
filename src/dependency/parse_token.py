from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import BaseModel, Field
from starlette import status

from src.core.config import settings
from src.utils.enums import AppType, UserRole


class UserToken(BaseModel):
    user_id: str | UUID
    name: str
    phone: str | None
    roles: set[str]
    email: str | None = None
    groups: list[str] = Field(default_factory=list)


def _raw_token(
    credentials: HTTPAuthorizationCredentials | str | None,
) -> str | None:
    if credentials is None:
        return None
    if isinstance(credentials, HTTPAuthorizationCredentials):
        return credentials.credentials
    return credentials or None


def _payload_to_user(payload: dict) -> UserToken:
    roles_raw = payload.get("roles") or []
    if not isinstance(roles_raw, list):
        roles_raw = []
    return UserToken(
        user_id=payload.get("uuid") or payload.get("sub") or "",
        name=payload.get("full_name_ru") or payload.get("name") or "Аноним",
        phone=payload.get("phone_mobile"),
        roles={str(r) for r in roles_raw},
        email=payload.get("email"),
        groups=list(payload.get("groups") or []),
    )


def _decode_jwt(raw: str) -> UserToken:
    try:
        payload = jwt.decode(
            raw,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
    return _payload_to_user(payload)


def _service_user() -> UserToken:
    return UserToken(
        user_id=UUID("00000000-0000-0000-0000-000000000000"),
        name="service",
        phone=None,
        roles=set(),
    )


def api_user_info(
    credentials: HTTPAuthorizationCredentials | str | None,
) -> UserToken:
    raw = _raw_token(credentials)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return _decode_jwt(raw)


def internal_user_info(token: str | None) -> UserToken:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return _decode_jwt(token)


def srv_user_info():
    pass


match settings.app_type:
    case AppType.api:
        scheme = HTTPBearer(auto_error=False)
        user_info = api_user_info
    case AppType.internal:
        scheme = APIKeyHeader(name="X-User-Token", auto_error=False)
        user_info = internal_user_info
    case _:
        scheme = HTTPBearer(auto_error=False)
        user_info = srv_user_info


def get_user_info(
    token: Annotated[
        HTTPAuthorizationCredentials | str | None,
        Depends(scheme),
    ],
) -> UserToken:
    return user_info(token)


class TokenVerify:
    def __init__(self, required_roles: list[UserRole] | None = None) -> None:
        self.required_roles = required_roles

    def __call__(
        self,
        token: Annotated[
            HTTPAuthorizationCredentials | str | None,
            Depends(scheme),
        ],
    ) -> UserToken:
        if settings.app_type == AppType.srv:
            return srv_user_info(token)

        user = user_info(token)
        self.check_permissions(user)
        return user

    def check_permissions(self, user: UserToken) -> None:
        if not self.required_roles:
            return
        if any(role.value in user.roles for role in self.required_roles):
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
