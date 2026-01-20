# app/models/product.py
from app.schemas.product import ProductResponse
from app.models.common import BaseMixin
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, String, Float, Integer, ForeignKey

if TYPE_CHECKING:
    from app.models.user import User


class Product(BaseMixin, Base):
    __tablename__ = "products"

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
        return ProductResponse.model_validate(self, from_attributes=True)
