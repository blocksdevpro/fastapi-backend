# app/schemas/user.py
from app.schemas.common import PasswordField
from datetime import datetime
from pydantic import BaseModel
from pydantic import Field, EmailStr
from typing import Optional, Annotated, Literal
from app.schemas.common import QueryParams, UUIDStr


class UserParams(QueryParams):
    sort_by: Annotated[
        Literal["created_at", "updated_at", "name", "email"],
        Field("created_at", description="Field to sort by"),
    ]


class CreateUserRequest(BaseModel):
    name: Annotated[str, Field(str, min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field(...)]
    password: PasswordField


class UpdateUserRequest(BaseModel):
    name: Annotated[str, Field(..., min_length=3, max_length=50)]


class UserResponse(BaseModel):
    id: UUIDStr
    name: Annotated[str, Field(...)]
    email: Annotated[EmailStr, Field(...)]
    role: Annotated[str, Field(...)]
    email_verified: Annotated[bool, Field(...)]

    created_at: Annotated[datetime, Field(...)]
    updated_at: Optional[Annotated[datetime, Field(...)]]
