from app.services.base import BaseService
from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from app.db.session import AsyncSession, get_session
from sqlalchemy import select
from app.models.user import User
from app.services.password import PasswordService
from app.schemas.auth import RefreshRequest, SignupRequest, LoginRequest, AuthResponse
from app.services.token import TokenService


class AuthService(BaseService):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
        password_service: Annotated[PasswordService, Depends()],
        token_service: Annotated[TokenService, Depends()],
    ):
        self.session = session
        self.password_service = password_service
        self.token_service = token_service
        super().__init__()

    async def _find_user(self, email: str) -> User:
        query = select(User).where(User.email == email)
        self.logger.info("Finding user with email: {}".format(email))

        return (await self.session.execute(query)).scalar_one_or_none()

    async def _create_user(self, name: str, email: str, password: str):
        user = User(name=name, email=email, hashed_password=password)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def signup(self, request: Request, payload: SignupRequest) -> AuthResponse:
        user = await self._find_user(payload.email)
        if user:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")

        hashed_password = await self.password_service.hash_password(payload.password)

        user = await self._create_user(payload.name, payload.email, hashed_password)
        tokens = await self.token_service.create_tokens(request, user)

        return AuthResponse(user=user.to_response(), tokens=tokens)

    async def login(self, request: Request, payload: LoginRequest) -> AuthResponse:
        user = await self._find_user(payload.email)
        if not user or not await self.password_service.verify_password(
            payload.password, user.hashed_password
        ):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

        tokens = await self.token_service.create_tokens(request, user)

        return AuthResponse(user=user.to_response(), tokens=tokens)

    async def refresh(self, request: Request, payload: RefreshRequest) -> AuthResponse:
        token = await self.token_service.validate_refresh_token(payload.refresh_token)
        user = await self._find_user(token.email)
        tokens = await self.token_service.create_tokens(request, user)

        return AuthResponse(
            user=user.to_response(),
            tokens=tokens,
        )
