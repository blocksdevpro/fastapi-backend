from fastapi import APIRouter

from app.handlers.response import response_handler


class AutoAPIResponseRouter(APIRouter):
    def add_api_route(self, path: str, endpoint, **kwargs):
        # Force response_model_exclude_unset for this CustomRouter
        kwargs.setdefault("response_model_exclude_none", True)

        # apply @response_handler decorater
        endpoint = response_handler()(endpoint)

        return super().add_api_route(path, endpoint, **kwargs)
