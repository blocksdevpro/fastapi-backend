
from fastapi import Depends, Request
from app.utils.router import AutoAPIResponseRouter
from app.dependencies import ProductServiceDependency, CurrentUserDependency
from app.schemas.common import QueryParams

router = AutoAPIResponseRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get("")
async def get_products(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    params: QueryParams = Depends(),
):
    return await service._find_products(user.id, params)
