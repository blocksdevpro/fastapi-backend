from fastapi import APIRouter

# Import your existing response_handler
from app.handlers.response import response_handler


class AutoAPIResponseRouter(APIRouter):
    def add_api_route(self, path: str, endpoint, **kwargs):
        # 1. Force the exclude_unset setting globally for all routes on this router
        kwargs.setdefault("response_model_exclude_unset", True)

        # 2. Automatically apply your @response_handler() decorator
        # This prevents you from having to write it manually on every route
        endpoint = response_handler()(endpoint)

        return super().add_api_route(path, endpoint, **kwargs)
