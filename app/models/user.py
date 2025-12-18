# app/models/user.py

from datetime import datetime
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, String, Boolean, DateTime, text
from app.models.common import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID,
        server_default=text("gen_random_uuid()"),
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)


    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"
    
    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"


    