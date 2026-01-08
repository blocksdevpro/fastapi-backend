from uuid import UUID
from typing import Optional
from fastapi.exceptions import HTTPException
from app.models.product import Product
from app.schemas.product import CreateProductRequest
from app.services.base import BaseService

from fastapi import Depends, status
from app.db.session import AsyncSession, get_session

from sqlalchemy import select, Select
from app.schemas.common import QueryParams
from sqlalchemy import asc, desc, or_, func


class ProductService(BaseService):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.model = Product
        super().__init__()

    async def _find_product(self, user_id: UUID, product_id: UUID):
        result = await self.session.execute(
            select(Product).where(Product.id == product_id, Product.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def _find_products(self, user_id: UUID, params: QueryParams):
        data_query = select(Product).where(Product.user_id == user_id)

        # apply filters
        data_query = self._apply_filters(data_query, params)

        # count total products.
        count_query = select(func.count()).select_from(data_query.subquery())

        # apply sorting
        data_query = self._apply_sorting(data_query, params)

        # apply pagination
        data_query = data_query.offset(params.offset).limit(params.limit)

        result = await self.session.execute(data_query)
        count_result = await self.session.execute(count_query)

        return {
            "items": result.scalars().all(),
            "metadata": {
                "pagination": {
                    "page": params.page,
                    "limit": params.limit,
                    "total": count_result.scalar(),
                }
            },
        }

    def _apply_filters(self, query: Select, params: QueryParams) -> Select:
        if params.query:
            query = query.where(
                or_(
                    self.model.name.ilike(f"%{params.query}%"),
                    self.model.description.ilike(f"%{params.query}%"),
                )
            )
        return query

    def _apply_sorting(self, query: Select, params: QueryParams) -> Select:
        sort_column = getattr(self.model, params.sort_by, "created_at")
        order_by = asc(sort_column) if params.sort_order == "asc" else desc(sort_column)

        return query.order_by(order_by)

    async def get_product(self, user_id: UUID, product_id: UUID):
        product = await self._find_product(user_id, product_id)
        if not product:
            self.logger.warning(f"Product not found {user_id=} {product_id=}.")
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found.")
        return product

    async def get_products(self, user_id: UUID, params: QueryParams):
        products = await self._find_products(user_id, params)
        if not products:
            self.logger.warning(f"Products not found {user_id=}.")
        return

    async def create_product(
        self, user_id: UUID, payload: CreateProductRequest
    ) -> Optional[Product]:
        product = Product(
            user_id=user_id,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            stock=payload.stock,
        )
        self.logger.info(f"Creating {product}")

        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product
