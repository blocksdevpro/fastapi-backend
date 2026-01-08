from uuid import UUID
from fastapi import Depends, Request
from app.schemas.product import CreateProductRequest
from app.utils.router import AutoAPIResponseRouter
from app.dependencies import ProductServiceDependency, CurrentUserDependency
from app.schemas.common import QueryParams
from app.schemas.response import APIResponse
from app.schemas.product import ProductResponse

router = AutoAPIResponseRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("", response_model=APIResponse[ProductResponse])
async def create_products(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    payload: CreateProductRequest,
):
    return await service.create_product(user.id, payload)


@router.get("", response_model=APIResponse[list[ProductResponse]])
async def get_products(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    params: QueryParams = Depends(),
):
    return await service.get_products(user.id, params)


@router.get("/{product_id}", response_model=APIResponse[ProductResponse])
async def get_product(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    product_id: UUID,
):
    return await service.get_product(user.id, product_id)
