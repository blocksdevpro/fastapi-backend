from app.core.messages import ErrorMessages
from app.services.base import BaseService
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status


class Token:
    def __init__(
        self,
        sub: str,
        email: str,
        token_type: str,
        iat: datetime | float,
        exp: datetime | float,
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

    def decode_token(self, token: str) -> Token:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Validate token type
            if payload.get("type") != self.token_type:
                self.logger.warning(
                    f"Token type mismatch. Expected: {self.token_type}, Got: {payload.get('type')}"
                )
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    ErrorMessages.INVALID_OR_EXPIRED_TOKEN.format(self.token_type),
                )

            return Token(
                sub=payload.get("sub", ""),
                email=payload.get("email", ""),
                token_type=payload.get("type", ""),
                iat=payload.get("iat", 0.0),
                exp=payload.get("exp", 0.0),
            )
        except JWTError:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                ErrorMessages.INVALID_OR_EXPIRED_TOKEN.format(self.token_type),
            )
