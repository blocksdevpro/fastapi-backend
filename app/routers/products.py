from app.schemas.product import ProductParams
from app.schemas.product import UpdateProductRequest
from typing import Annotated
from uuid import UUID
from fastapi import Depends, Request, Query
from app.schemas.product import CreateProductRequest
from app.utils.router import AutoAPIResponseRouter
from app.dependencies import ProductServiceDependency, CurrentUserDependency
from app.schemas.response import APIResponse
from app.schemas.product import ProductResponse

router = AutoAPIResponseRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=APIResponse[ProductResponse],
    summary="Create a new product",
    description="Create a new product with the provided details.",
)
async def create_products(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    payload: CreateProductRequest,
):
    """
    Create a new product.

    This endpoint creates a new product associated with the specific user.
    """
    return await service.create_product(user.id, payload)


@router.get(
    "",
    response_model=APIResponse[list[ProductResponse]],
    summary="Get all products",
    description="Retrieve a paginated list of all products.",
)
async def get_products(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    params: ProductParams = Depends(),
):
    """
    Get all products.

    This endpoint retrieves all products created by the user.
    """
    return await service.get_products(user.id, params)


@router.get(
    "/{product_id}",
    response_model=APIResponse[ProductResponse],
    summary="Get product by ID",
    description="Retrieve a specific product by its unique ID.",
)
async def get_product(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    product_id: UUID,
):
    """
    Get product by ID.

    This endpoint retrieves the details of a specific product.
    """
    return await service.get_product(user.id, product_id)


@router.delete(
    "",
    response_model=APIResponse,
    summary="Delete products",
    description="Delete one or multiple products by their IDs.",
)
async def delete_products(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    product_ids: Annotated[list[UUID], Query()],
):
    """
    Delete products.

    This endpoint allows deleting multiple products at once.
    """
    return await service.delete_products(user.id, product_ids)


@router.put(
    "/{product_id}",
    response_model=APIResponse[ProductResponse],
    summary="Update product",
    description="Update an existing product with new details.",
)
async def update_product(
    request: Request,
    user: CurrentUserDependency,
    service: ProductServiceDependency,
    product_id: UUID,
    payload: UpdateProductRequest,
):
    """
    Update product.

    This endpoint allows updating the details of an existing product.
    """
    return await service.update_product(user.id, product_id, payload)
