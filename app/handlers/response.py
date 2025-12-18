from typing import Callable, Any, Union
from functools import wraps
from fastapi.exceptions import HTTPException
from app.schemas.response import APIResponse, Error, ErrorDetail

def response_handler() -> APIResponse:
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(status_code=500, detail="Internal Server Error")

            if isinstance(result, APIResponse):
                return result
            if isinstance(result, dict) and (hasattr(result, "metadata") and hasattr(result, "data")):
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
