# app/schemas/user.py
from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: str | UUID
    name: str
    email: str

    created_at: datetime
    updated_at: Optional[datetime]
