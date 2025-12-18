# app/schemas/user.py
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

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
