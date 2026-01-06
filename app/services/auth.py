from uuid import UUID
from sqlalchemy.exc import IntegrityError
from app.models.session import Session
from app.services.base import BaseService
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Request, status
from app.db.session import AsyncSession, get_session
from sqlalchemy import select
from app.models.user import User
from app.services.password import PasswordService
from app.schemas.auth import (
    MessageResponse,
    RefreshRequest,
    SignupRequest,
    LoginRequest,
    AuthResponse,
)
from app.schemas.user import UpdateUserRequest

from app.services.session import Token, SessionService


class AuthService(BaseService):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
        password_service: Annotated[PasswordService, Depends()],
        session_service: Annotated[SessionService, Depends()],
    ):
        self.session = session
        self.password_service = password_service
        self.session_service = session_service
        super().__init__()

    async def _find_user(self, email: str) -> Optional[User]:
        self.logger.info("Finding user with email: {}".format(email))
        query = select(User).where(User.email == email)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _find_user_by_id(self, user_id: str) -> Optional[User]:
        self.logger.info("Finding user with user_id: {}".format(user_id))
        query = select(User).where(User.id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: str) -> User:
        user = await self._find_user_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return user

    async def _create_user(self, name: str, email: str, password: str):
        user = User(name=name, email=email, hashed_password=password)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def signup(self, request: Request, payload: SignupRequest) -> AuthResponse:
        try:
            hashed_password = await self.password_service.hash_password(
                payload.password
            )
            user = await self._create_user(payload.name, payload.email, hashed_password)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")

        tokens = await self.session_service.create_tokens(request, user)

        return AuthResponse(user=user.to_response(), tokens=tokens)

    async def login(self, request: Request, payload: LoginRequest) -> AuthResponse:
        user = await self._find_user(payload.email)
        if not user or not await self.password_service.verify_password(
            payload.password, user.hashed_password
        ):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

        tokens = await self.session_service.create_tokens(request, user)

        return AuthResponse(user=user.to_response(), tokens=tokens)

    async def refresh(self, request: Request, payload: RefreshRequest) -> AuthResponse:
        token, session = await self.session_service.validate_refresh_token(
            payload.refresh_token
        )
        user = await self._get_user_by_id(token.sub)
        tokens = await self.session_service.create_tokens(request, user, session.id)

        return AuthResponse(
            user=user.to_response(),
            tokens=tokens,
        )

    async def logout(
        self, request: Request, payload: RefreshRequest
    ) -> MessageResponse:
        return await self.session_service.revoke_refresh_token(payload.refresh_token)

    async def current_user(self, token: Token) -> User:
        user = await self._find_user_by_id(token.sub)
        if not user:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid or expired access token"
            )
        return user

    async def get_sessions(self, user: User) -> list[Session]:
        return await self.session_service.find_active_sessions(user.id)

    async def revoke(self, user: User, session_id: UUID) -> MessageResponse:
        return await self.session_service.revoke_session(user.id, session_id)

    async def update(self, user: User, payload: UpdateUserRequest) -> User:
        user.name = payload.name

        await self.session.commit()
        await self.session.refresh(user)
        return user
