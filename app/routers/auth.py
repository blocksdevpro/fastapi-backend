# app/routers/auth.py

from uuid import UUID
from fastapi import Request, Path

from app.dependencies import (
    AuthServiceDependency,
    CurrentUserDependency,
    CurrentUserTokenDependency,
)
from app.schemas.auth import (
    AuthResponse,
    MessageResponse,
    RefreshRequest,
    SessionResponse,
    SignupRequest,
    LoginRequest,
)

from app.schemas.response import APIResponse
from app.schemas.user import UserResponse, UpdateUserRequest
from app.utils.router import AutoAPIResponseRouter

router = AutoAPIResponseRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=APIResponse[AuthResponse])
async def signup(
    request: Request, payload: SignupRequest, auth_service: AuthServiceDependency
):
    return await auth_service.signup(request, payload)


@router.post("/login", response_model=APIResponse[AuthResponse])
async def login(
    request: Request, payload: LoginRequest, auth_service: AuthServiceDependency
):
    return await auth_service.login(request, payload)


@router.post("/refresh", response_model=APIResponse[AuthResponse])
async def refresh(
    request: Request, payload: RefreshRequest, auth_service: AuthServiceDependency
):
    return await auth_service.refresh(request, payload)


@router.post("/logout", response_model=APIResponse[MessageResponse])
async def logout(
    request: Request,
    payload: RefreshRequest,
    auth_service: AuthServiceDependency,
    user: CurrentUserDependency,
):
    return await auth_service.logout(request, payload)


@router.get("/me", response_model=APIResponse[UserResponse])
async def current_user(
    request: Request,
    token: CurrentUserTokenDependency,
    auth_service: AuthServiceDependency,
):
    return await auth_service.current_user(token)


@router.get("/sessions", response_model=APIResponse[list[SessionResponse]])
async def sessions(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
):
    return await auth_service.get_sessions(user)


@router.post("/revoke", response_model=APIResponse[MessageResponse])
async def revoke(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    session_id: UUID = Path(..., description="Session ID to revoke"),
):
    return await auth_service.revoke(user, session_id)


@router.put("/update", response_model=APIResponse[UserResponse])
async def update(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    payload: UpdateUserRequest,
):
    return await auth_service.update(user, payload)
