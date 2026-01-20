# app/handlers/response.py

from app.core.messages import ErrorMessages
from slowapi.errors import RateLimitExceeded
from functools import wraps
from typing import Any, Callable, Union
from fastapi.exceptions import HTTPException
from app.schemas.response import APIResponse

import logging

logger = logging.getLogger(__name__)


def transform_model_to_response(model: Any) -> Union[Any, list[Any], dict[str, Any]]:
    if hasattr(model, "to_response") and callable(model.to_response):
        return model.to_response()
    elif isinstance(model, list):
        return [transform_model_to_response(item) for item in model]
    elif isinstance(model, dict) and "items" in model:
        model["items"] = [transform_model_to_response(item) for item in model["items"]]

    return model


def response_handler() -> Callable:
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
            except (HTTPException, RateLimitExceeded):
                raise
            except Exception as e:
                logger.exception(f"Unhandled error in {func.__name__}: {e}")
                raise HTTPException(
                    status_code=500, detail=ErrorMessages.INTERNAL_SERVER_ERROR
                )

            # transform models using their to_response() func.
            result = transform_model_to_response(result)

            if isinstance(result, APIResponse):
                return result

            if isinstance(result, dict) and (
                "metadata" in result and "items" in result
            ):
                return APIResponse(
                    success=True,
                    data=result["items"],
                    meta=result["metadata"],
                )

            return APIResponse(
                success=True,
                data=result,
            )

        return wrapper

    return decorator
