from uuid import UUID
from fastapi import Request, Path, BackgroundTasks

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


@router.post(
    "/signup",
    response_model=APIResponse[AuthResponse],
    summary="Register a new user",
    description="Create a new user account with the provided details.",
)
async def signup(
    request: Request, payload: SignupRequest, auth_service: AuthServiceDependency
):
    """
    Register a new user.

    This endpoint creates a new user account.
    """
    return await auth_service.signup(request, payload)


@router.post(
    "/login",
    response_model=APIResponse[AuthResponse],
    summary="Login user",
    description="Authenticate a user and return an access token and refresh token.",
)
async def login(
    request: Request, payload: LoginRequest, auth_service: AuthServiceDependency
):
    """
    Login user.

    This endpoint authenticates a user with their email and password.
    """
    return await auth_service.login(request, payload)


@router.post(
    "/refresh",
    response_model=APIResponse[AuthResponse],
    summary="Refresh access token",
    description="Use a refresh token to obtain a new access token.",
)
async def refresh(
    request: Request, payload: RefreshRequest, auth_service: AuthServiceDependency
):
    """
    Refresh access token.

    This endpoint allows using a valid refresh token to get a new access token.
    """
    return await auth_service.refresh(request, payload)


@router.post(
    "/logout",
    response_model=APIResponse[MessageResponse],
    summary="Logout user",
    description="Invalidate the current session/token.",
)
async def logout(
    request: Request,
    payload: RefreshRequest,
    auth_service: AuthServiceDependency,
    user: CurrentUserDependency,
):
    """
    Logout user.

    This endpoint invalidates the provided refresh token, effectively logging the user out.
    """
    return await auth_service.logout(request, payload)


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get current user",
    description="Retrieve the profile information of the currently authenticated user.",
)
async def current_user(
    request: Request,
    token: CurrentUserTokenDependency,
    auth_service: AuthServiceDependency,
):
    """
    Get current user.

    This endpoint returns the details of the currently logged-in user.
    """
    return await auth_service.current_user(token)


@router.get(
    "/sessions",
    response_model=APIResponse[list[SessionResponse]],
    summary="Get active sessions",
    description="Retrieve a list of all active sessions for the current user.",
)
async def sessions(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
):
    """
    Get active sessions.

    This endpoint returns all active sessions associated with the user.
    """
    return await auth_service.get_sessions(user)


@router.post(
    "/revoke/{session_id}",
    response_model=APIResponse[MessageResponse],
    summary="Revoke session",
    description="Revoke a specific session by its ID.",
)
async def revoke(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    session_id: UUID = Path(..., description="Session ID to revoke"),
):
    """
    Revoke session.

    This endpoint allows the user to revoke (cancel) a specific session.
    """
    return await auth_service.revoke(user, session_id)


@router.patch(
    "/update",
    response_model=APIResponse[UserResponse],
    summary="Update user profile",
    description="Update information of the currently authenticated user.",
)
async def update(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    payload: UpdateUserRequest,
):
    """
    Update user profile.

    This endpoint allows the user to update their profile information.
    """
    return await auth_service.update(user, payload)


@router.post(
    "/forget-password",
    response_model=APIResponse[MessageResponse],
    summary="Request password reset",
    description="Initiate the password reset process by sending a reset link to the user's email.",
)
@limiter.limit("5/minute")
async def forget_password(
    request: Request,
    payload: ForgetPasswordRequest,
    auth_service: AuthServiceDependency,
    background_tasks: BackgroundTasks,
):
    """
    Request password reset.

    This endpoint sends a password reset link to the provided email address, if it exists.
    """
    return await auth_service.forget_password(request, payload, background_tasks)


@router.post(
    "/reset-password",
    response_model=APIResponse[MessageResponse],
    summary="Reset password",
    description="Reset the user's password using the token received via email.",
)
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    auth_service: AuthServiceDependency,
):
    """
    Reset password.

    This endpoint resets the user's password using a valid reset token.
    """
    return await auth_service.reset_password(request, payload)


@router.post(
    "/change-password",
    response_model=APIResponse[MessageResponse],
    summary="Change password",
    description="Change the password for the currently authenticated user.",
)
async def change_password(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    payload: ChangePasswordRequest,
):
    """
    Change password.

    This endpoint allows an authenticated user to change their password.
    """
    return await auth_service.change_password(request, user, payload)


@router.post(
    "/send-verification-email",
    response_model=APIResponse[MessageResponse],
    summary="Send verification email",
    description="Send a verification email to the currently logged-in user.",
)
@limiter.limit("5/minute")
async def send_verification_email(
    request: Request,
    user: CurrentUserDependency,
    auth_service: AuthServiceDependency,
    background_tasks: BackgroundTasks,
):
    """Send email verification link to the currently logged-in user."""
    return await auth_service.send_verification_email(user, background_tasks)


@router.post(
    "/verify-email",
    response_model=APIResponse[MessageResponse],
    summary="Verify email",
    description="Verify the user's email address using the provided token.",
)
async def verify_email(
    request: Request,
    payload: VerifyEmailRequest,
    auth_service: AuthServiceDependency,
):
    """Verify email using the token from the verification email."""
    return await auth_service.verify_email(request, payload)
