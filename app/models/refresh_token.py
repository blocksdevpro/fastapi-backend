# app/models/refresh_token.py

from datetime import datetime
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String, text
from app.models.common import TimestampMixin


class RefreshToken(TimestampMixin, Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(
        UUID, server_default=text("gen_random_uuid()"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_id: Mapped[str] = mapped_column(String(255), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    ip_address: Mapped[str] = mapped_column(String(45))  # IPv6 max length
    user_agent: Mapped[str] = mapped_column(String(500))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

    def to_response(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "device_id": self.device_id,
            "ip_address": self.ip_address,
            "last_used_at": self.last_used_at,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
