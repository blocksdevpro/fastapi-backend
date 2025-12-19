import hashlib
from app.models.user import User
from app.schemas.auth import TokenResponse
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
                    status.HTTP_401_UNAUTHORIZED, f"Invalid {self.token_type} token!"
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
                status.HTTP_401_UNAUTHORIZED, f"Invalid {self.token_type} token!"
            )


class TokenService(BaseService):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session
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

    def _hash_str(string: str) -> str:
        return hashlib.sha256(string.encode()).hexdigest()

    def _hash_token(self, token: Token, token_str: str):
        return self._hash_str(f"{token_str}-{token.sub}-{token.iat}")

    def _extract_ip_address(self, request: Request):
        headers = request.headers
        for header in ["CF-Connecting-IP", "X-Real-IP", "X-Forwarded-For"]:
            ip_address: str = headers.get(header)
            if ip_address:
                if header == "X-Forwarded-For":
                    ip_address = ip_address.split(",")[0].strip()
                return ip_address
        return getattr(request.client, "host", "Unknown")

    def _generate_device_id(self, request: Request):
        ip_address = self._extract_ip_address(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        accept_language = request.headers.get("Accept-Language", "Unknown")
        accept_encoding = request.headers.get("Accept-Encoding", "Unknown")

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
        return self.refresh_token_service.decode_token(token)

    async def create_tokens(
        self, request: Request, user: User, access_only=False
    ) -> TokenResponse:
        payload = {"sub": str(user.id), "email": user.email}

        access_token = await self._create_access_token(payload)
        refresh_token = "" if access_only else await self._create_refresh_token(payload)
        token_type = "refresh" if access_only else "bearer"

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
        )
