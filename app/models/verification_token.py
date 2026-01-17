# app/models/verification_token.py

from app.models.common import BaseMixin
from enum import Enum
from uuid import UUID as PyUUID
from datetime import datetime
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, String, Index


class TokenType(str, Enum):
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class VerificationToken(BaseMixin, Base):
    __tablename__ = "verification_tokens"

    user_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    token_type: Mapped[str] = mapped_column(String(50), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Composite index for efficient cleanup queries
    __table_args__ = (
        Index("ix_verification_tokens_user_type_used", "user_id", "token_type", "used"),
    )

    def __repr__(self):
        return f"VerificationToken(id={self.id}, user_id={self.user_id}, type={self.token_type}, used={self.used})"

    def __str__(self):
        return f"VerificationToken(id={self.id}, user_id={self.user_id}, type={self.token_type}, used={self.used})"
