import logging


class BaseService:
    def __init__(self):
        self.logger = logging.getLogger(f"Main.{self.__class__.__name__}")
