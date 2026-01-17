# app/models/common.py

from sqlalchemy import text
from sqlalchemy import UUID
from uuid import UUID as PyUUID
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class BaseIDMixin:
    id: Mapped[PyUUID] = mapped_column(
        UUID, server_default=text("gen_random_uuid()"), primary_key=True
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.timezone("utc", func.now()), index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.timezone("utc", func.now()),
        nullable=True,
        index=True,
    )


class BaseMixin(BaseIDMixin, TimestampMixin):
    pass
