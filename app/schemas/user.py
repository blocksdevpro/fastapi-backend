# app/schemas/user.py
from datetime import datetime
from pydantic import BaseModel
from pydantic import Field, EmailStr
from typing import Optional, Annotated, Literal
from pydantic import field_validator
import re
from app.schemas.common import QueryParams


class UserParams(QueryParams):
    sort_by: Annotated[
        Literal["created_at", "updated_at", "name", "email"],
        Field("created_at", description="Field to sort by"),
    ]


class UserCreate(BaseModel):
    name: Annotated[str, Field(str, min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field(...)]
    password: Annotated[str, Field(..., min_length=8, max_length=24)]

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


class UpdateUserRequest(BaseModel):
    name: Annotated[str, Field(..., min_length=3, max_length=50)]


class UserResponse(BaseModel):
    id: Annotated[str, Field(...)]
    name: Annotated[str, Field(...)]
    email: Annotated[EmailStr, Field(...)]
    role: Annotated[str, Field(...)]
    email_verified: Annotated[bool, Field(...)]

    created_at: Annotated[datetime, Field(...)]
    updated_at: Optional[Annotated[datetime, Field(...)]]
