import re
from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, Field, EmailStr, AfterValidator
from app.schemas.user import UserResponse


def password_validator(password: str) -> str:
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


# Create a reusable type
PasswordField = Annotated[
    str, Field(..., min_length=8, max_length=24), AfterValidator(password_validator)
]


class SignupRequest(BaseModel):
    name: Annotated[str, Field(..., min_length=3, max_length=50, examples=["John Doe"])]
    email: Annotated[EmailStr, Field(..., examples=["john.doe@example.com"])]
    password: PasswordField


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., examples=["john.doe@example.com"])]
    password: PasswordField


class RefreshRequest(BaseModel):
    refresh_token: Annotated[
        str,
        Field(
            ...,
            examples=["<refresh_token>"],
        ),
    ]


class ForgetPasswordRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., examples=["john.doe@example.com"])]


class ChangePasswordRequest(BaseModel):
    old_password: PasswordField
    new_password: PasswordField


class ResetPasswordRequest(BaseModel):
    token: Annotated[
        str, Field(..., min_length=32, max_length=64, examples=["abc123..."])
    ]
    password: PasswordField


class VerifyEmailRequest(BaseModel):
    token: Annotated[
        str, Field(..., min_length=32, max_length=64, examples=["abc123..."])
    ]


class TokenResponse(BaseModel):
    access_token: Annotated[
        str,
        Field(
            ...,
            examples=["<access_token>"],
        ),
    ]
    refresh_token: Annotated[
        str,
        Field(
            ...,
            examples=["<refresh_token>"],
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
