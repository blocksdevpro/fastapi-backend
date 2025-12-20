# app/routers/auth.py

from fastapi import APIRouter, Request

from app.dependencies import AuthServiceDependency, CurrentUserTokenDependency
from app.schemas.auth import AuthResponse, RefreshRequest, SignupRequest, LoginRequest

from app.handlers.response import response_handler
from app.schemas.response import APIResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=APIResponse[AuthResponse])
@response_handler()
async def signup(
    request: Request, payload: SignupRequest, auth_service: AuthServiceDependency
):
    return await auth_service.signup(request, payload)


@router.post("/login", response_model=APIResponse[AuthResponse])
@response_handler()
async def login(
    request: Request, payload: LoginRequest, auth_service: AuthServiceDependency
):
    return await auth_service.login(request, payload)


@router.post("/refresh", response_model=APIResponse[AuthResponse])
@response_handler()
async def refresh(
    request: Request, payload: RefreshRequest, auth_service: AuthServiceDependency
):
    return await auth_service.refresh(request, payload)


@router.get("/me", response_model=APIResponse[UserResponse])
@response_handler()
async def current_user(
    request: Request,
    token: CurrentUserTokenDependency,
    auth_service: AuthServiceDependency,
):
    return await auth_service.current_user(token)
