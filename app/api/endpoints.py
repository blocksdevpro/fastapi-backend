from sqlalchemy import text
from fastapi import APIRouter
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.core.config import settings
from app.dependencies import SessionDependency


router = APIRouter(prefix=settings.API_V1_PREFIX)


router.include_router(users_router)
router.include_router(auth_router)
router.include_router(products_router)


@router.get("/health")
async def health_check(session: SessionDependency):
    try:
        # Check database connection
        await session.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.VERSION,
        "services": {
            "database": db_status
        }
    }