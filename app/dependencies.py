# app/dependencies.py

from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.db.session import get_session, AsyncSession
from app.models.user import User
from app.services.auth.auth import AuthService
from app.services.auth.password import PasswordService
from app.services.auth.session import Token, SessionService
from app.services.product import ProductService
from app.services.user import UserService

from app.core.security import get_bearer_token


BearerTokenDependency = Annotated[str, Depends(get_bearer_token)]

SessionDependency = Annotated[AsyncSession, Depends(get_session)]
AuthServiceDependency = Annotated[AuthService, Depends()]
PasswordServiceDependency = Annotated[PasswordService, Depends()]
SessionServiceDependency = Annotated[SessionService, Depends()]
ProductServiceDependency = Annotated[ProductService, Depends()]
UserServiceDependency = Annotated[UserService, Depends()]


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


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency that requires the current user to be an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


CurrentUserTokenDependency = Annotated[Token, Depends(get_current_user_payload)]
CurrentUserDependency = Annotated[User, Depends(get_current_user)]
CurrentAdminUserDependency = Annotated[User, Depends(get_current_admin_user)]
