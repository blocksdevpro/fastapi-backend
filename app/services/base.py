import logging
from app.db.session import Base

from typing import TypeVar

T = TypeVar("T", bound=Base)


class BaseService:
    def __init__(self):
        self.logger = logging.getLogger(f"Main.{self.__class__.__name__}")
