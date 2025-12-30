import hashlib
import re

from sqlalchemy import delete, not_, select, update
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import MessageResponse, TokenResponse
from app.services.base import BaseService
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from jose import jwt, JWTError
from typing import Optional
from app.db.session import AsyncSession, get_session
from typing import Annotated
from fastapi import Depends
from fastapi import HTTPException, status, Request


class Token:
    def __init__(
        self, sub: str, email: str, token_type: str, iat: datetime, exp: datetime
    ):
        self.sub = sub
        self.email = email
        self.type = token_type
        self.iat = iat
        self.exp = exp

    def get(self, key: str, default=None):
        return getattr(self, key, default)


class JwtService(BaseService):
    def __init__(
        self, token_type: str, secret_key: str, algorithm: str, expire_minutes: int
    ):
        self.token_type = token_type
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

        super().__init__()

    def encode_token(self, data: dict) -> str:
        payload = data.copy()
        current_time = datetime.now(timezone.utc)

        payload.update(
            {
                "type": self.token_type,
                "iat": current_time,
                "exp": current_time + timedelta(minutes=self.expire_minutes),
            }
        )

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Token]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Validate token type
            if payload.get("type") != self.token_type:
                self.logger.warning(
                    f"Token type mismatch. Expected: {self.token_type}, Got: {payload.get('type')}"
                )
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    f"Invalid or expired {self.token_type} token!",
                )

            return Token(
                sub=payload.get("sub"),
                email=payload.get("email"),
                token_type=payload.get("type"),
                iat=payload.get("iat"),
                exp=payload.get("exp"),
            )
        except JWTError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                f"Invalid or expired {self.token_type} token!",
            )


class TokenService(BaseService):
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
            ip_address: str = headers.get(header)
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

    async def validate_refresh_token(self, token: str) -> Token:
        token_payload = self.refresh_token_service.decode_token(token)
        token_hash = self._hash_token(token_payload, token)
        refresh_token = await self._find_refresh_token(token_hash)
        if not refresh_token:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token!"
            )
        return token_payload

    async def _find_refresh_token(self, token_hash: str) -> RefreshToken:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash, not_(RefreshToken.revoked)
            )
        )
        return result.scalar_one_or_none()

    async def _find_user_session(self, user_id: str, session_id: str) -> RefreshToken:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.id == session_id,
                not_(RefreshToken.revoked),
            )
        )
        return result.scalar_one_or_none()

    async def create_tokens(
        self, request: Request, user: User, refresh=False
    ) -> TokenResponse:
        payload = {"sub": str(user.id), "email": user.email}

        access_token = await self._create_access_token(payload)
        refresh_token = "" if refresh else await self._create_refresh_token(payload)
        token_type = "refresh" if refresh else "bearer"

        if not refresh:
            await self.save_refresh_token(request, refresh_token, user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
        )

    async def cleanup_device_tokens(self, user_id: str, device_id: str) -> None:
        await self.session.execute(
            delete(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.device_id == device_id,
            )
        )

    async def cleanup_max_device_tokens(self, user_id: str) -> None:
        subquery = (
            select(RefreshToken.id)
            .where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.last_used_at.desc())
            .offset(self.max_active_sessions)
        )

        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.id.in_(subquery))
            .values(revoked=True)
        )

    async def cleanup_expired_tokens(self, user_id: str) -> None:
        current_time = datetime.now(timezone.utc)
        await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.expires_at < current_time,
            )
            .values(revoked=True)
        )
        await self.session.commit()

    async def save_refresh_token(
        self, request: Request, token: str, user_id: str
    ) -> None:
        try:
            token_payload = self.refresh_token_service.decode_token(token)
            token_hash = self._hash_token(token_payload, token)
            device_id = self._generate_device_id(request)
            ip_address = self._extract_ip_address(request)
            user_agent = request.headers.get("User-Agent", "Unknown")[:500]  # Truncate

            await self.cleanup_expired_tokens(user_id)
            await self.cleanup_device_tokens(user_id, device_id)
            await self.cleanup_max_device_tokens(user_id)

            refresh_token = RefreshToken(
                user_id=user_id,
                device_id=device_id,
                token_hash=token_hash,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.fromtimestamp(token_payload.exp, timezone.utc),
                last_used_at=datetime.now(timezone.utc),
            )

            self.session.add(refresh_token)
            await self.session.commit()
        except Exception:
            self.logger.error(
                f"Error while saving refresh_token with token_hash={token_hash}"
            )
            await self.session.rollback()
            raise

    async def update_refresh_token_usage(
        self, token: Token, token_str: str, user_id: str
    ):
        token_hash = self._hash_token(token, token_str)
        await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash, RefreshToken.user_id == user_id
            )
            .values(last_used_at=datetime.now(timezone.utc))
        )

    async def revoke_refresh_token(self, token: str) -> MessageResponse:
        token_payload = self.refresh_token_service.decode_token(token)
        token_hash = self._hash_token(token_payload, token)

        await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == token_payload.sub,
                not_(RefreshToken.revoked),
            )
            .values(revoked=True)
        )
        await self.session.commit()
        return MessageResponse(message="Successfully logged out of the session!")

    async def find_active_sessions(self, user_id: str):
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id, not_(RefreshToken.revoked))
            .limit(10)
        )
        return result.scalars().all()

    async def revoke_session(self, user_id: str, session_id: str):
        session = await self._find_user_session(user_id, session_id)
        if session:
            await self.session.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id, RefreshToken.id == session_id)
                .values(revoked=True)
            )
            await self.session.commit()
        return MessageResponse(message="Successfully revoked the session!")
