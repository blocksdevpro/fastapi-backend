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
    ResetPasswordRequest,
    ChangePasswordRequest,
    ForgetPasswordRequest,
    VerifyEmailRequest,
)

from app.schemas.response import APIResponse
from app.schemas.user import UserResponse, UpdateUserRequest
from app.utils.router import AutoAPIResponseRouter

from app.core.slowapi import limiter

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


@router.post("/revoke/{session_id}", response_model=APIResponse[MessageResponse])
async def revoke(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    session_id: UUID = Path(..., description="Session ID to revoke"),
):
    return await auth_service.revoke(user, session_id)


@router.patch("/update", response_model=APIResponse[UserResponse])
async def update(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    payload: UpdateUserRequest,
):
    return await auth_service.update(user, payload)


@router.post("/forget-password", response_model=APIResponse[MessageResponse])
@limiter.limit("5/minute")
async def forget_password(
    request: Request,
    payload: ForgetPasswordRequest,
    auth_service: AuthServiceDependency,
):
    return await auth_service.forget_password(request, payload)


@router.post("/reset-password", response_model=APIResponse[MessageResponse])
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    auth_service: AuthServiceDependency,
):
    return await auth_service.reset_password(request, payload)


@router.post("/change-password", response_model=APIResponse[MessageResponse])
async def change_password(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    payload: ChangePasswordRequest,
):
    return await auth_service.change_password(request, user, payload)


@router.post("/send-verification-email", response_model=APIResponse[MessageResponse])
@limiter.limit("5/minute")
async def send_verification_email(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
):
    """Send email verification link to the currently logged-in user."""
    return await auth_service.send_verification_email(user)


@router.post("/verify-email", response_model=APIResponse[MessageResponse])
async def verify_email(
    request: Request,
    payload: VerifyEmailRequest,
    auth_service: AuthServiceDependency,
):
    """Verify email using the token from the verification email."""
    return await auth_service.verify_email(request, payload)
