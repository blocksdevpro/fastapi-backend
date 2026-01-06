# app/models/product.py
from uuid import UUID as PyUUID
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, String, Boolean, text, Float, Integer, ForeignKey
from app.models.common import TimestampMixin
import typing
if typing.TYPE_CHECKING:
    from app.models.user import User

class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[PyUUID] = mapped_column(
        UUID, server_default=text("gen_random_uuid()"), primary_key=True
    )
    user_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="products")

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, description={self.description} price={self.price} stock={self.stock})"

    def __str__(self):
        return f"Product(id={self.id}, name={self.name}, description={self.description} price={self.price} stock={self.stock})"

    def to_response(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
