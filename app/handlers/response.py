from functools import wraps
from typing import Any, Callable, Union
from fastapi.exceptions import HTTPException
from app.schemas.response import APIResponse

import logging

logger = logging.getLogger(__name__)


def to_response_handler(model: Any) -> Union[Any, list[Any], dict[str, Any]]:
    if hasattr(model, "to_response") and callable(model.to_response):
        return model.to_response()
    elif isinstance(model, list):
        return [to_response_handler(item) for item in model]
    elif isinstance(model, dict) and hasattr(model, "items"):
        model["items"] = [to_response_handler(item) for item in model["items"]]

    return model


def response_handler() -> Callable:
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.error("Internal Server Error: {}".format(e))
                raise HTTPException(status_code=500, detail="Internal Server Error")

            result = to_response_handler(result)

            if isinstance(result, APIResponse):
                return result

            if isinstance(result, dict) and (
                hasattr(result, "metadata") and hasattr(result, "items")
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
