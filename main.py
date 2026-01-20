from app.core.config import settings
from fastapi import FastAPI
from app.core.slowapi import limiter

# import middlewares
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.handlers.middlewares import RequestIDMiddleware, RequestDurationMiddleware

# import routers
from app.api.endpoints import router as api_router

# import exception handlers
from app.handlers.exception import (
    http_exception_handler,
    validation_exception_handler,
    rate_limit_exception_handler,
)
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import HTTPException, RequestValidationError

# import and call configure_logging.

from app.core.logger import configure_logging

configure_logging()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url=settings.API_V1_PREFIX + "/docs",
    redoc_url=settings.API_V1_PREFIX + "/redoc",
)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestDurationMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(api_router)

app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)  # type: ignore



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
