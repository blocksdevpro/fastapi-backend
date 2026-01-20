# app/services/auth/verification.py

from app.core.messages import ErrorMessages
import secrets
import hashlib
from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Annotated

from sqlalchemy import select, update, delete
from fastapi import Depends, HTTPException, status

from app.core.config import settings
from app.db.session import AsyncSession, get_session
from app.models.verification_token import VerificationToken, TokenType
from app.services.base import BaseService


class VerificationService(BaseService):
    """
    Handles creation, validation, and consumption of verification tokens.

    Security features:
    - Cryptographically secure token generation (secrets.token_urlsafe)
    - SHA256 hashing of tokens before storage
    - Single-use enforcement via 'used' flag
    - Automatic invalidation of old tokens when creating new ones
    - Expiration-based token validity
    """

    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
        self.secret = settings.VERIFICATION_TOKEN_SECRET
        super().__init__()

    def _hash_token(self, token: str) -> str:
        """Hash token with secret for secure storage."""
        return hashlib.sha256(f"{token}-{self.secret}".encode()).hexdigest()

    def _get_expiry_minutes(self, token_type: TokenType) -> int:
        """Get expiration minutes based on token type."""
        if token_type == TokenType.PASSWORD_RESET:
            return settings.PASSWORD_RESET_EXPIRE_MINUTES
        elif token_type == TokenType.EMAIL_VERIFICATION:
            return settings.EMAIL_VERIFICATION_EXPIRE_MINUTES
        return 15  # Default fallback

    async def _invalidate_existing_tokens(
        self, user_id: UUID, token_type: TokenType
    ) -> None:
        """Invalidate any existing unused tokens of the same type for the user."""
        await self.session.execute(
            update(VerificationToken)
            .where(
                VerificationToken.user_id == user_id,
                VerificationToken.token_type == token_type.value,
                VerificationToken.used.is_(False),
            )
            .values(used=True)
        )

    async def create_token(self, user_id: UUID, token_type: TokenType) -> str:
        """
        Create a new verification token.

        1. Invalidates any existing tokens of same type for user
        2. Generates cryptographically secure random token
        3. Hashes token and stores in database
        4. Returns raw token (only time it exists in plaintext)

        Args:
            user_id: The user's UUID
            token_type: Type of token (password_reset or email_verification)

        Returns:
            The raw token string to be sent to user
        """
        try:
            # Invalidate existing tokens of the same type
            await self._invalidate_existing_tokens(user_id, token_type)

            # Generate cryptographically secure token (256-bit entropy)
            raw_token = secrets.token_urlsafe(32)
            token_hash = self._hash_token(raw_token)

            # Calculate expiration
            expire_minutes = self._get_expiry_minutes(token_type)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

            # Create token record
            verification_token = VerificationToken(
                user_id=user_id,
                token_hash=token_hash,
                token_type=token_type.value,
                expires_at=expires_at,
                used=False,
            )

            self.session.add(verification_token)
            await self.session.commit()

            self.logger.info(
                f"Created {token_type.value} token for user {user_id}, expires at {expires_at}"
            )

            return raw_token

        except Exception as e:
            self.logger.error(f"Error creating verification token: {str(e)}")
            await self.session.rollback()
            raise

    async def verify_token(
        self, token: str, token_type: TokenType
    ) -> VerificationToken:
        """
        Verify a token is valid.

        Checks:
        - Token hash matches
        - Token type matches
        - Token is not used
        - Token is not expired

        Args:
            token: The raw token string from user
            token_type: Expected token type

        Returns:
            The VerificationToken record if valid

        Raises:
            HTTPException: If token is invalid or expired
        """
        token_hash = self._hash_token(token)
        current_time = datetime.now(timezone.utc)

        result = await self.session.execute(
            select(VerificationToken).where(
                VerificationToken.token_hash == token_hash,
                VerificationToken.token_type == token_type.value,
                VerificationToken.used.is_(False),
                VerificationToken.expires_at > current_time,
            )
        )

        token_record = result.scalar_one_or_none()

        if not token_record:
            self.logger.warning(f"Invalid or expired {token_type.value} token attempt")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.INVALID_OR_EXPIRED_TOKEN.format(token_type.value),
            )

        return token_record

    async def consume_token(self, token_record: VerificationToken) -> None:
        """
        Mark a token as used (single-use enforcement).

        Args:
            token_record: The VerificationToken to consume
        """
        token_record.used = True
        await self.session.commit()
        self.logger.info(
            f"Consumed {token_record.token_type} token for user {token_record.user_id}"
        )

    async def cleanup_expired_tokens(self) -> int:
        """
        Delete expired and used tokens from database.

        This can be called via a scheduled job/cron to keep the table clean.

        Returns:
            Number of tokens deleted
        """
        current_time = datetime.now(timezone.utc)

        result = await self.session.execute(
            delete(VerificationToken).where(
                (VerificationToken.expires_at < current_time)
                | (VerificationToken.used.is_(True))
            )
        )

        await self.session.commit()
        deleted_count = result.rowcount  # type: ignore

        self.logger.info(f"Cleaned up {deleted_count} expired/used verification tokens")
        return deleted_count
