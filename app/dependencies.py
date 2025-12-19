# app/dependencies.py

from typing import Annotated
from fastapi import Depends
from app.db.session import get_session, AsyncSession
from app.services.auth import AuthService
from app.services.user import UserService

SessionDependency = Annotated[AsyncSession, Depends(get_session)]
UserServiceDependency = Annotated[UserService, Depends()]
AuthServiceDependency = Annotated[AuthService, Depends()]
