from app.schemas.response import APIResponse, Error, ErrorDetail
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError, HTTPException


def http_exception_handler(request: Request, exception: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content=APIResponse(
            success=False,
            error=Error(code=exception.status_code, message=exception.detail),
        ).model_dump(),
    )


def rate_limit_exception_handler(
    request: Request, exception: RateLimitExceeded
) -> JSONResponse:
    response = JSONResponse(
        status_code=exception.status_code,
        content=APIResponse(
            success=False,
            error=Error(code=exception.status_code, message=exception.detail),
        ).model_dump(),
    )
    response = request.app.state.rate_limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response


def validation_exception_handler(
    request: Request, exception: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            success=False,
            error=Error(
                code=422,
                message="Validation Error",
                details=[
                    ErrorDetail(field=".".join(error["loc"]), message=error["msg"])
                    for error in exception.errors()
                ],
            ),
        ).model_dump(),
    )
