import asyncio
from functools import partial
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PasswordService:
    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=3,
            memory_cost=102400,  # 100 MB
            parallelism=2,
        )

    async def _run(self, func, *args):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args))

    async def hash_password(self, password: str) -> str:
        return await self._run(self.ph.hash, password)

    async def verify_password(self, password: str, hashed: str) -> bool:
        try:
            return await self._run(self.ph.verify, hashed, password)
        except VerifyMismatchError:
            return False
