from typing import Optional
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
    refresh_token: Optional[str]
    token_type: str


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
