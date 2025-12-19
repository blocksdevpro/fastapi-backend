from typing import Callable
from functools import wraps
from fastapi.exceptions import HTTPException
from app.schemas.response import APIResponse

import logging

logger = logging.getLogger(__name__)


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

            if isinstance(result, APIResponse):
                return result
            if isinstance(result, dict) and (
                hasattr(result, "metadata") and hasattr(result, "data")
            ):
                return APIResponse(
                    success=True,
                    data=result["data"],
                    meta=result["metadata"],
                )

            return APIResponse(
                success=True,
                data=result,
            )

        return wrapper

    return decorator
