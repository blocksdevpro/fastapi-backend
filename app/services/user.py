from app.schemas.user import UserParams
from fastapi.exceptions import HTTPException
from app.models.user import User
from app.services.base import BaseService
from app.db.session import AsyncSession, get_session
from fastapi import Depends, status
from sqlalchemy import select, Select, or_, asc, desc, func
from uuid import UUID


class UserService(BaseService):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
        self.model = User
        super().__init__()

    def _apply_filters(self, query: Select, params: UserParams) -> Select:
        if params.query:
            query = query.where(
                or_(
                    self.model.name.ilike(f"%{params.query}%"),
                    self.model.email.ilike(f"%{params.query}%"),
                )
            )
        return query

    def _apply_sorting(self, query: Select, params: UserParams) -> Select:
        sort_column = getattr(self.model, params.sort_by, "created_at")
        order_by = asc(sort_column) if params.sort_order == "asc" else desc(sort_column)

        return query.order_by(order_by)

    async def _find_user(self, user_id: UUID):
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def _find_users(self, params: UserParams):
        query = select(User)
        query = self._apply_filters(query, params)
        query = self._apply_sorting(query, params)
        count_query = select(func.count()).select_from(query.subquery())

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        items = result.scalars().all()
        count = count_result.scalar()
        self.logger.info(f"Found {count} users returned {len(items)} users.")

        return {
            "items": items,
            "metadata": {
                "pagination": {
                    "page": params.page,
                    "limit": params.limit,
                    "total": count,
                }
            },
        }

    async def get_user(self, user_id: UUID):
        user = await self._find_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def get_users(self, query_params: UserParams):
        return await self._find_users(query_params)
