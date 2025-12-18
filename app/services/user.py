# app/services/user.py

from app.services.base import BaseService
from app.db.session import AsyncSession, get_session
from app.models.user import User
from typing import Annotated
from fastapi import Depends
from sqlalchemy import select
from app.schemas.user import UserCreate
from uuid import UUID

class UserService(BaseService):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        super().__init__()
        self.session = session
    
    async def get_users(self):
        self.logger.info("Getting users")
        return (await self.session.execute(select(User))).scalars().all()

    async def get_user(self, user_id: UUID):
        self.logger.info("Getting user with id: {}".format(user_id))
        return (await self.session.execute(select(User).where(User.id == user_id))).scalar()
    
    async def create_user(self, payload: UserCreate):
        self.logger.info("Creating user with name: {}".format(payload.name))
        user = User(
            name=payload.name,
            email=payload.email,
            hashed_password=payload.password
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        self.logger.info("User created with id: {}".format(user.id))
        return user
    