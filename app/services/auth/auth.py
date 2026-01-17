from uuid import UUID
from sqlalchemy.exc import IntegrityError
from app.models.session import Session
from app.services.base import BaseService
from typing import Annotated, Optional, Sequence
from fastapi import Depends, HTTPException, Request, status
from app.db.session import AsyncSession, get_session
from sqlalchemy import select
from app.models.user import User
from app.models.verification_token import TokenType
from app.services.auth.password import PasswordService
from app.services.auth.verification import VerificationService
from app.services.email import EmailService
from app.schemas.auth import (
    MessageResponse,
    AuthResponse,
)
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    RefreshRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
    ForgetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.user import UpdateUserRequest

from app.services.auth.session import Token, SessionService


class AuthService(BaseService):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
        password_service: Annotated[PasswordService, Depends()],
        session_service: Annotated[SessionService, Depends()],
        verification_service: Annotated[VerificationService, Depends()],
        email_service: Annotated[EmailService, Depends()],
    ):
        self.session = session
        self.password_service = password_service
        self.session_service = session_service
        self.verification_service = verification_service
        self.email_service = email_service
        super().__init__()

    async def _find_user(self, email: str) -> Optional[User]:
        self.logger.info(f"Finding user with {email=}")
        query = select(User).where(User.email == email)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _find_user_by_id(self, user_id: UUID) -> Optional[User]:
        self.logger.info(f"Finding user with {user_id=}")
        query = select(User).where(User.id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: UUID) -> User:
        user = await self._find_user_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return user

    async def _create_user(self, name: str, email: str, password: str):
        user = User(name=name, email=email, password_hash=password)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def signup(self, request: Request, payload: SignupRequest) -> AuthResponse:
        try:
            password_hash = await self.password_service.hash_password(payload.password)
            user = await self._create_user(payload.name, payload.email, password_hash)
        except IntegrityError:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already exists")

        tokens = await self.session_service.create_tokens(request, user)

        return AuthResponse(user=user.to_response(), tokens=tokens)

    async def login(self, request: Request, payload: LoginRequest) -> AuthResponse:
        user = await self._find_user(payload.email)
        if not user or not await self.password_service.verify_password(
            payload.password,
            user.password_hash,  # pyrefly: ignore [bad-argument-type]
        ):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

        tokens = await self.session_service.create_tokens(request, user)

        return AuthResponse(user=user.to_response(), tokens=tokens)

    async def refresh(self, request: Request, payload: RefreshRequest) -> AuthResponse:
        token, session = await self.session_service.validate_refresh_token(
            payload.refresh_token
        )
        user = await self._get_user_by_id(
            token.sub  # pyrefly: ignore [bad-argument-type]
        )
        tokens = await self.session_service.create_tokens(
            request,
            user,
            session.id,  # pyrefly: ignore [bad-argument-type]
        )

        return AuthResponse(
            user=user.to_response(),
            tokens=tokens,
        )

    async def logout(
        self, request: Request, payload: RefreshRequest
    ) -> MessageResponse:
        return await self.session_service.revoke_refresh_token(payload.refresh_token)

    async def current_user(self, token: Token) -> User:
        user = await self._find_user_by_id(
            token.sub  # pyrefly: ignore [bad-argument-type]
        )
        if not user:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid or expired access token"
            )
        return user

    async def get_sessions(self, user: User) -> Sequence[Session]:
        return await self.session_service.find_active_sessions(
            user.id  # pyrefly: ignore [bad-argument-type]
        )

    async def revoke(self, user: User, session_id: UUID) -> MessageResponse:
        return await self.session_service.revoke_session(
            user.id,  # pyrefly: ignore [bad-argument-type]
            session_id,
        )

    async def update(self, user: User, payload: UpdateUserRequest) -> User:
        user.name = payload.name

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def forget_password(
        self, request: Request, payload: ForgetPasswordRequest
    ) -> MessageResponse:
        user = await self._find_user(payload.email)
        # Security: Always return success message to prevent email enumeration
        if user:
            token = await self.verification_service.create_token(
                user.id,  # pyrefly: ignore [bad-argument-type]
                TokenType.PASSWORD_RESET,
            )
            await self.email_service.send_password_reset_email(user.email, token)
        return MessageResponse(
            message="If the email exists, a password reset link has been sent."
        )

    async def reset_password(
        self, request: Request, payload: ResetPasswordRequest
    ) -> MessageResponse:
        # Verify the token and get the token record
        token_record = await self.verification_service.verify_token(
            payload.token, TokenType.PASSWORD_RESET
        )
        # Get the user associated with the token
        user = await self._get_user_by_id(token_record.user_id)
        # Update the password
        user.password_hash = await self.password_service.hash_password(payload.password)
        # Consume the token (single-use)
        await self.verification_service.consume_token(token_record)
        await self.session.commit()
        return MessageResponse(message="Password reset successfully")

    async def send_verification_email(self, user: User) -> MessageResponse:
        """Send email verification link to the current user."""
        if user.email_verified:
            return MessageResponse(message="Email is already verified.")

        token = await self.verification_service.create_token(
            user.id,  # pyrefly: ignore [bad-argument-type]
            TokenType.EMAIL_VERIFICATION,
        )
        await self.email_service.send_verification_email(
            user.email,  # pyrefly: ignore [bad-argument-type]
            token,
        )
        return MessageResponse(message="Verification email sent.")

    async def verify_email(
        self, request: Request, payload: VerifyEmailRequest
    ) -> MessageResponse:
        """Verify user's email using token from email link."""
        # Verify the token
        token_record = await self.verification_service.verify_token(
            payload.token, TokenType.EMAIL_VERIFICATION
        )
        # Get the user and mark email as verified
        user = await self._get_user_by_id(token_record.user_id)
        user.email_verified = True
        # Consume the token
        await self.verification_service.consume_token(token_record)
        await self.session.commit()
        return MessageResponse(message="Email verified successfully.")

    async def change_password(
        self, request: Request, user: User, payload: ChangePasswordRequest
    ) -> MessageResponse:
        if not await self.password_service.verify_password(
            payload.old_password,
            user.password_hash,  # pyrefly: ignore [bad-argument-type]
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid old password")

        user.password_hash = await self.password_service.hash_password(
            payload.new_password
        )

        await self.session.commit()
        await self.session.refresh(user)

        return MessageResponse(message="Password changed successfully")
