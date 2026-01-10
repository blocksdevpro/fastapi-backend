# app/dependencies.py

from typing import Annotated
from fastapi import Depends
from app.db.session import get_session, AsyncSession
from app.models.user import User
from app.services.auth.auth import AuthService
from app.services.auth.password import PasswordService
from app.services.auth.session import Token, SessionService
from app.services.product import ProductService

from app.core.security import get_bearer_token


BearerTokenDependency = Annotated[str, Depends(get_bearer_token)]

SessionDependency = Annotated[AsyncSession, Depends(get_session)]
AuthServiceDependency = Annotated[AuthService, Depends()]
PasswordServiceDependency = Annotated[PasswordService, Depends()]
SessionServiceDependency = Annotated[SessionService, Depends()]
ProductServiceDependency = Annotated[ProductService, Depends()]


async def get_current_user_payload(
    token: BearerTokenDependency,
    session_service: SessionServiceDependency,
) -> Token:
    return await session_service.validate_access_token(token)


async def get_current_user(
    token: Annotated[Token, Depends(get_current_user_payload)],
    auth_service: AuthServiceDependency,
) -> User:
    return await auth_service.current_user(token)


CurrentUserTokenDependency = Annotated[Token, Depends(get_current_user_payload)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]
