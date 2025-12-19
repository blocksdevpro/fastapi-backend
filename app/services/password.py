import asyncio
from functools import partial
from app.core.config import settings
from passlib.context import CryptContext
from app.services.base import BaseService
from typing import Callable, Optional


class PasswordService(BaseService):
    def __init__(self):
        self.context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS
        )
        super().__init__()

    async def _handle_async(
        self,
        func: Callable,
        args: Optional[tuple] = tuple(),
        kwargs: Optional[dict] = dict(),
    ):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def hash_password(self, password: str):
        return await self._handle_async(self.context.hash, (password,))

    async def verify_password(self, password: str, hashed_password: str):
        return await self._handle_async(
            self.context.verify, (password, hashed_password)
        )
