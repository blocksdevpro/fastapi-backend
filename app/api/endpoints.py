from fastapi import APIRouter
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router


router = APIRouter(prefix="/api")


router.include_router(users_router)
router.include_router(auth_router)
router.include_router(products_router)
