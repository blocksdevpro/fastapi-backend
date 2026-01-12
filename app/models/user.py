# app/models/user.py

from enum import Enum
from uuid import UUID as PyUUID
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, String, Boolean, text, Enum as SQLAlchemyEnum
from app.models.common import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product


class UserRole(str, Enum):
    """Enum for user roles"""

    USER = "user"
    ADMIN = "admin"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(
        UUID, server_default=text("gen_random_uuid()"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.USER
    )

    products: Mapped[list["Product"]] = relationship("Product", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    def to_response(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
