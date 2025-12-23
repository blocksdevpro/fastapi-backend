from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.slowapi import limiter

# import routers
from app.routers.auth import router as auth_router
# from app.routers.users import router as users_router


# import exception handlers
from app.handlers.exception import (
    http_exception_handler,
    validation_exception_handler,
    rate_limit_exception_handler,
)
from fastapi.exceptions import HTTPException, RequestValidationError
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    from sqlalchemy import text
    from app.db.session import async_engine, Base

    async with async_engine.begin() as connection:
        await connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        await connection.run_sync(Base.metadata.create_all)
    yield

    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
# app.include_router(users_router)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)


@app.get("/health")
async def read_health():
    return {"status": "HEALTHY"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
