from typing import Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from app.schemas.user import UserResponse


class SignupRequest(BaseModel):
    name: Annotated[str, Field(..., min_length=3, max_length=50, examples=["John Doe"])]
    email: Annotated[EmailStr, Field(..., examples=["john.doe@example.com"])]
    password: Annotated[
        str, Field(..., min_length=8, max_length=24, examples=["Pass123!"])
    ]

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if " " in password:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")

        return password


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., examples=["john.doe@example.com"])]
    password: Annotated[
        str, Field(..., min_length=8, max_length=24, examples=["Pass123!"])
    ]

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if " " in password:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")

        return password


class RefreshRequest(BaseModel):
    refresh_token: Annotated[
        str,
        Field(
            ...,
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            ],
        ),
    ]


class ForgetPasswordRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., examples=["john.doe@example.com"])]


class ChangePasswordRequest(BaseModel):
    old_password: Annotated[
        str, Field(..., min_length=8, max_length=24, examples=["Pass123!"])
    ]
    new_password: Annotated[
        str, Field(..., min_length=8, max_length=24, examples=["Pass123!"])
    ]

    @field_validator("old_password", "new_password")
    @classmethod
    def validate_passwords(cls, password: str) -> str:
        if " " in password:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")

        return password


class ResetPasswordRequest(BaseModel):
    token: Annotated[
        str, Field(..., min_length=32, max_length=64, examples=["abc123..."])
    ]
    password: Annotated[
        str, Field(..., min_length=8, max_length=24, examples=["Pass123!"])
    ]

    @field_validator("password")
    @classmethod
    def validate_passwords(cls, password: str) -> str:
        if " " in password:
            raise ValueError("Password must not contain spaces")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")

        return password


class VerifyEmailRequest(BaseModel):
    token: Annotated[
        str, Field(..., min_length=32, max_length=64, examples=["abc123..."])
    ]


class TokenResponse(BaseModel):
    access_token: Annotated[
        str,
        Field(
            ...,
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            ],
        ),
    ]
    refresh_token: Annotated[
        str,
        Field(
            ...,
            examples=[
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
            ],
        ),
    ]
    token_type: Annotated[str, Field(..., examples=["bearer"])]


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseModel):
    message: Annotated[str, Field(...)]


class SessionResponse(BaseModel):
    id: Annotated[str, Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])]
    user_id: Annotated[
        str, Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    ]
    device_id: Annotated[str, Field(..., examples=["1908b47bf9ed06f5"])]
    ip_address: Annotated[str, Field(..., examples=["127.0.0.1"])]
    expires_at: Annotated[datetime, Field(..., examples=["2026-01-06T12:27:39.123456"])]
    created_at: Annotated[datetime, Field(..., examples=["2026-01-06T12:27:39.123456"])]
    updated_at: Optional[
        Annotated[datetime, Field(..., examples=["2026-01-06T12:27:39.123456"])]
    ]
