# app/dependencies.py

from typing import Annotated
from fastapi import Depends
from app.db.session import get_session, AsyncSession
from app.models.user import User
from app.services.auth import AuthService
from app.services.user import UserService
from app.services.password import PasswordService
from app.services.token import Token, TokenService

from app.core.security import get_bearer_token


BearerTokenDependency = Annotated[str, Depends(get_bearer_token)]

SessionDependency = Annotated[AsyncSession, Depends(get_session)]
UserServiceDependency = Annotated[UserService, Depends()]
AuthServiceDependency = Annotated[AuthService, Depends()]
PasswordServiceDependency = Annotated[PasswordService, Depends()]
TokenServiceDependency = Annotated[TokenService, Depends()]


async def get_current_user_payload(
    token: BearerTokenDependency,
    token_service: TokenServiceDependency,
) -> Token:
    return await token_service.validate_access_token(token)


async def get_current_user(
    token: Annotated[Token, Depends(get_current_user_payload)],
    auth_service: AuthServiceDependency,
) -> User:
    return await auth_service.current_user(token)


CurrentUserTokenDependency = Annotated[Token, Depends(get_current_user_payload)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]
