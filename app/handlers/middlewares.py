import logging
import time
import uuid
from fastapi import Request, Response
from app.core.logger import request_id_ctx
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("Main.RequestLogMiddleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx.set(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RequestDurationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()

        response = await call_next(request)

        request_duration = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Request {request.method} {request.url.path} took {request_duration:.2f}ms"
        )
        response.headers["X-Request-Duration-Ms"] = str(request_duration)
        return response
