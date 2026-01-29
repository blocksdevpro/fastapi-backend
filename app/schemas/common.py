import re
from pydantic import BaseModel, Field
from typing import Literal, Optional, Annotated
from pydantic import BeforeValidator, PlainSerializer, AfterValidator
from uuid import UUID


class QueryParams(BaseModel):
    query: Annotated[Optional[str], Field("", description="Search query")]
    page: Annotated[int, Field(1, ge=1, description="Page number")]
    limit: Annotated[
        int, Field(10, ge=1, le=100, description="Number of items per page")
    ]

    sort_by: Annotated[
        Literal["created_at", "updated_at"],
        Field("created_at", description="Field to sort by"),
    ]
    sort_order: Annotated[
        Literal["asc", "desc"], Field("desc", description="Sort order")
    ]

    @property
    def offset(self):
        return (self.page - 1) * self.limit


# Functions


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


def validate_uuid(value):
    """Convert string or UUID to UUID"""
    if isinstance(value, str):
        return UUID(value)
    return value


def serialize_uuid(value):
    """Convert UUID to string"""
    return str(value)


# Reusable types

# Create a reusable UUID string type
UUIDStr = Annotated[
    UUID,
    BeforeValidator(validate_uuid),
    PlainSerializer(serialize_uuid, return_type=str),
]

# reusable type for Password
PasswordField = Annotated[
    str, Field(..., min_length=8, max_length=24), AfterValidator(password_validator)
]
