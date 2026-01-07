from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.slowapi import limiter

# import middlewares
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.handlers.middlewares import RequestIDMiddleware, RequestDurationMiddleware
# import routers
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    from sqlalchemy import text
    from app.db.session import async_engine, Base

    async with async_engine.begin() as connection:
        await connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await connection.run_sync(Base.metadata.create_all)
    yield

    await async_engine.dispose()


app = FastAPI(
    title="Calorine API",
    description="Calorie tracking backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)
app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestDurationMiddleware)

app.include_router(auth_router)
app.include_router(products_router)

app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)  # type: ignore


@app.get("/health")
async def read_health():
    return {"status": "HEALTHY"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
