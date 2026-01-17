from fastapi import APIRouter
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.core.config import settings


router = APIRouter(prefix=settings.API_V1_PREFIX)


router.include_router(users_router)
router.include_router(auth_router)
router.include_router(products_router)
