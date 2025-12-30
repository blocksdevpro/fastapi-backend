from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import UserResponse


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseModel):
    message: str


class SessionResponse(BaseModel):
    id: str | UUID
    user_id: str
    device_id: str
    ip_address: str
    expires_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]
