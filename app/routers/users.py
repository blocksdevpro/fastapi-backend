from app.schemas.user import UserParams
from app.dependencies import UserServiceDependency
from fastapi import Request, Depends

from app.utils.router import AutoAPIResponseRouter
from app.dependencies import CurrentAdminUserDependency
from app.schemas.user import UserResponse
from app.schemas.response import APIResponse


router = AutoAPIResponseRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=APIResponse[list[UserResponse]],
    summary="Get all users",
    description="Retrieve a paginated list of all users. Requires admin privileges.",
)
async def get_users(
    request: Request,
    current_admin_user: CurrentAdminUserDependency,
    service: UserServiceDependency,
    params: UserParams = Depends(),
):
    """
    Retrieve all users.

    This endpoint returns a list of all users in the system.
    It is restricted to admin users only.
    """
    return await service.get_users(params)
