import re
import hashlib
from uuid import UUID
from datetime import datetime, timezone
from typing import Annotated, Optional
from sqlalchemy import not_, select, update, delete
from fastapi import Depends, Request, HTTPException, status

from app.models.user import User
from app.models.session import Session
from app.core.config import settings
from app.services.base import BaseService
from app.services.token import Token, JwtService
from app.db.session import AsyncSession, get_session
from app.schemas.auth import TokenResponse, MessageResponse
from typing import Sequence


class SessionService(BaseService):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
        self.max_active_sessions = settings.MAX_ACTIVE_SESSIONS
        self.access_token_service = JwtService(
            "access",
            settings.JWT_ACCESS_SECRET_KEY,
            settings.JWT_ALGORITHM,
            settings.JWT_ACCESS_EXPIRE_MINUTES,
        )
        self.refresh_token_service = JwtService(
            "refresh",
            settings.JWT_REFRESH_SECRET_KEY,
            settings.JWT_ALGORITHM,
            settings.JWT_REFRESH_EXPIRE_MINUTES,
        )

        super().__init__()

    def _hash_str(self, string: str) -> str:
        return hashlib.sha256(string.encode()).hexdigest()

    def _hash_token(self, token: Token, token_str: str) -> str:
        return self._hash_str(f"{token_str}-{token.sub}-{token.iat}")

    def _sanitize_header(self, value: str, max_length: int = 500) -> str:
        """Remove potentially dangerous characters from headers"""
        return re.sub(r"[^\w\s\-.,/()[\]]", "", value)[:max_length]

    def _extract_ip_address(self, request: Request) -> str:
        headers = request.headers
        for header in ["CF-Connecting-IP", "X-Real-IP", "X-Forwarded-For"]:
            ip_address: str | None = headers.get(header)
            if ip_address:
                if header == "X-Forwarded-For":
                    ip_address = ip_address.split(",")[0].strip()
                return ip_address
        return getattr(request.client, "host", "Unknown")

    def _generate_device_id(self, request: Request) -> str:
        ip_address = self._extract_ip_address(request)
        user_agent = self._sanitize_header(request.headers.get("User-Agent", "Unknown"))
        accept_language = self._sanitize_header(
            request.headers.get("Accept-Language", "Unknown")
        )
        accept_encoding = self._sanitize_header(
            request.headers.get("Accept-Encoding", "Unknown")
        )

        device_signature = self._hash_str(
            f"{ip_address}-{user_agent}-{accept_language}-{accept_encoding}"
        )[:16]

        return device_signature

    async def _create_access_token(self, data: dict) -> str:
        return self.access_token_service.encode_token(data)

    async def _create_refresh_token(self, data: dict) -> str:
        return self.refresh_token_service.encode_token(data)

    async def validate_access_token(self, token: str) -> Token:
        return self.access_token_service.decode_token(token)

    async def validate_refresh_token(self, token: str) -> tuple[Token, Session]:
        token_payload = self.refresh_token_service.decode_token(token)
        token_hash = self._hash_token(token_payload, token)
        session = await self._find_session(token_hash)
        if not session:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token!"
            )
        return token_payload, session

    async def _find_session(self, token_hash: str) -> Optional[Session]:
        result = await self.session.execute(
            select(Session).where(
                Session.token_hash == token_hash, not_(Session.revoked)
            )
        )
        return result.scalar_one_or_none()

    async def _find_user_session(
        self, user_id: UUID, session_id: UUID
    ) -> Optional[Session]:
        result = await self.session.execute(
            select(Session).where(
                Session.user_id == user_id,
                Session.id == session_id,
                not_(Session.revoked),
            )
        )
        return result.scalar_one_or_none()

    async def create_tokens(
        self, request: Request, user: User, session_id: Optional[UUID] = None
    ) -> TokenResponse:
        payload = {"sub": str(user.id), "email": user.email}

        access_token = await self._create_access_token(payload)
        refresh_token = await self._create_refresh_token(payload)

        # pyrefly: ignore [bad-argument-type]
        await self._create_session(request, refresh_token, user.id)
        if session_id:
            # pyrefly: ignore [bad-argument-type]
            await self._revoke_session(user.id, session_id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def cleanup_device_sessions(self, user_id: UUID, device_id: str) -> None:
        await self.session.execute(
            delete(Session).where(
                Session.user_id == user_id,
                Session.device_id == device_id,
            )
        )

    async def cleanup_max_device_sessions(self, user_id: UUID) -> None:
        subquery = (
            select(Session.id)
            .where(Session.user_id == user_id)
            .order_by(Session.created_at.desc())
            .offset(self.max_active_sessions)
        )

        await self.session.execute(
            update(Session).where(Session.id.in_(subquery)).values(revoked=True)
        )

    async def cleanup_expired_sessions(self, user_id: UUID) -> None:
        current_time = datetime.now(timezone.utc)
        await self.session.execute(
            update(Session)
            .where(
                Session.user_id == user_id,
                Session.expires_at < current_time,
            )
            .values(revoked=True)
        )
        await self.session.commit()

    async def _create_session(
        self, request: Request, token: str, user_id: UUID
    ) -> None:
        try:
            token_payload = self.refresh_token_service.decode_token(token)
            token_hash = self._hash_token(token_payload, token)
            device_id = self._generate_device_id(request)
            ip_address = self._extract_ip_address(request)
            user_agent = request.headers.get("User-Agent", "Unknown")[:500]  # Truncate

            self.logger.info(f"User logged_in with {device_id=}")

            await self.cleanup_expired_sessions(user_id)
            await self.cleanup_device_sessions(user_id, device_id)
            await self.cleanup_max_device_sessions(user_id)

            session = Session(
                user_id=user_id,
                device_id=device_id,
                token_hash=token_hash,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.fromtimestamp(token_payload.exp, timezone.utc),  # type: ignore
            )

            self.session.add(session)
            await self.session.commit()
        except Exception:
            self.logger.error(f"Error while saving session with {user_id=}")
            await self.session.rollback()
            raise

    async def revoke_refresh_token(self, token: str) -> MessageResponse:
        token_payload = self.refresh_token_service.decode_token(token)
        token_hash = self._hash_token(token_payload, token)

        await self.session.execute(
            update(Session)
            .where(
                Session.token_hash == token_hash,
                Session.user_id == token_payload.sub,
                not_(Session.revoked),
            )
            .values(revoked=True)
        )
        await self.session.commit()
        return MessageResponse(message="Successfully logged out of the session!")

    async def find_active_sessions(self, user_id: UUID) -> Sequence[Session]:
        result = await self.session.execute(
            select(Session)
            .where(Session.user_id == user_id, not_(Session.revoked))
            .limit(10)
        )
        return result.scalars().all()

    async def _revoke_session(self, user_id: UUID, session_id: UUID):
        await self.session.execute(
            update(Session)
            .where(Session.id == session_id, Session.user_id == user_id)
            .values(revoked=True)
        )
        await self.session.commit()

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> MessageResponse:
        session = await self._find_user_session(user_id, session_id)
        if session:
            await self._revoke_session(user_id, session_id)
        return MessageResponse(message="Successfully revoked the session!")
