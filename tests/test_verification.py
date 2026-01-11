"""
Tests for verification token functionality.

Tests cover:
- Password reset flow (forget password, reset with token)
- Email verification flow (send verification, verify email)
- Token validation (invalid/expired tokens)
"""

import pytest
from httpx import AsyncClient, Response
from unittest.mock import patch, AsyncMock

from app.schemas.auth import AuthResponse, SignupRequest


# Test user credentials for verification tests
verification_user = {
    "name": "VerifyUser",
    "email": "verify@test.com",
    "password": "Pass!123",
}

auth_tokens: AuthResponse


# ============================================================================
# Setup: Create a test user
# ============================================================================


@pytest.mark.asyncio(loop_scope="session")
async def test_create_verification_test_user(client: AsyncClient):
    """Create a user for verification tests."""
    res: Response = await client.post(
        "/auth/signup",
        json=SignupRequest(**verification_user).model_dump(),
    )
    assert res.status_code == 200

    global auth_tokens
    auth_tokens = AuthResponse(**res.json()["data"])


# ============================================================================
# Password Reset Flow Tests
# ============================================================================


@pytest.mark.asyncio(loop_scope="session")
async def test_forget_password_existing_user(client: AsyncClient):
    """Test forget password with existing email."""
    with patch(
        "app.services.email.EmailService.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send:
        res = await client.post(
            "/auth/forget-password",
            json={"email": verification_user["email"]},
        )

        assert res.status_code == 200
        res_json = res.json()
        assert res_json["success"]
        assert "password reset link" in res_json["data"]["message"].lower()

        # Verify email was sent
        mock_send.assert_called_once()


@pytest.mark.asyncio(loop_scope="session")
async def test_forget_password_nonexistent_user(client: AsyncClient):
    """Test forget password with non-existent email (should not reveal if user exists)."""
    with patch(
        "app.services.email.EmailService.send_password_reset_email",
        new_callable=AsyncMock,
    ) as mock_send:
        res = await client.post(
            "/auth/forget-password",
            json={"email": "nonexistent@test.com"},
        )

        assert res.status_code == 200
        res_json = res.json()
        assert res_json["success"]
        # Should return same message to prevent email enumeration
        assert "password reset link" in res_json["data"]["message"].lower()

        # Email should NOT be sent for non-existent user
        mock_send.assert_not_called()


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_invalid_token(client: AsyncClient):
    """Test reset password with invalid token."""
    res = await client.post(
        "/auth/reset-password",
        json={
            "token": "invalid_token_that_is_definitely_long_enough_to_pass_validation",
            "password": "NewPass!123",
        },
    )

    assert res.status_code == 400
    res_json = res.json()
    assert not res_json["success"]
    assert "invalid or expired token" in res_json["error"]["message"].lower()


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_flow_success(client: AsyncClient):
    """Test complete password reset flow with mocked email."""
    captured_token = None

    async def capture_token(to: str, token: str):
        nonlocal captured_token
        captured_token = token

    with patch(
        "app.services.email.EmailService.send_password_reset_email",
        side_effect=capture_token,
    ):
        # Step 1: Request password reset
        res = await client.post(
            "/auth/forget-password",
            json={"email": verification_user["email"]},
        )
        assert res.status_code == 200
        assert captured_token is not None

    # Step 2: Reset password with captured token
    new_password = "NewPass!456"
    res = await client.post(
        "/auth/reset-password",
        json={
            "token": captured_token,
            "password": new_password,
        },
    )

    assert res.status_code == 200
    res_json = res.json()
    assert res_json["success"]
    assert "password reset successfully" in res_json["data"]["message"].lower()

    # Step 3: Verify can login with new password
    res = await client.post(
        "/auth/login",
        json={"email": verification_user["email"], "password": new_password},
    )
    assert res.status_code == 200

    # Update global tokens and credentials for subsequent tests
    global auth_tokens
    auth_tokens = AuthResponse(**res.json()["data"])
    verification_user["password"] = new_password


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_token_single_use(client: AsyncClient):
    """Test that password reset tokens can only be used once."""
    captured_token = None

    async def capture_token(to: str, token: str):
        nonlocal captured_token
        captured_token = token

    with patch(
        "app.services.email.EmailService.send_password_reset_email",
        side_effect=capture_token,
    ):
        res = await client.post(
            "/auth/forget-password",
            json={"email": verification_user["email"]},
        )
        assert res.status_code == 200
        assert captured_token is not None

    # First use should succeed
    res = await client.post(
        "/auth/reset-password",
        json={
            "token": captured_token,
            "password": "NewPass!789",
        },
    )
    assert res.status_code == 200

    # Second use should fail (token already consumed)
    res = await client.post(
        "/auth/reset-password",
        json={
            "token": captured_token,
            "password": "AnotherPass!123",
        },
    )
    assert res.status_code == 400
    assert "invalid or expired token" in res.json()["error"]["message"].lower()

    # Update password for subsequent tests
    verification_user["password"] = "NewPass!789"


# ============================================================================
# Email Verification Flow Tests
# ============================================================================


@pytest.mark.asyncio(loop_scope="session")
async def test_send_verification_email_requires_auth(client: AsyncClient):
    """Test that sending verification email requires authentication."""
    res = await client.post("/auth/send-verification-email")
    assert res.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_send_verification_email_success(client: AsyncClient):
    """Test sending verification email to authenticated user."""
    # First login to get fresh tokens
    res = await client.post(
        "/auth/login",
        json={
            "email": verification_user["email"],
            "password": verification_user["password"],
        },
    )
    assert res.status_code == 200

    global auth_tokens
    auth_tokens = AuthResponse(**res.json()["data"])

    with patch(
        "app.services.email.EmailService.send_verification_email",
        new_callable=AsyncMock,
    ) as mock_send:
        res = await client.post(
            "/auth/send-verification-email",
            headers={"Authorization": f"Bearer {auth_tokens.tokens.access_token}"},
        )

        assert res.status_code == 200
        res_json = res.json()
        assert res_json["success"]
        assert "verification email sent" in res_json["data"]["message"].lower()

        mock_send.assert_called_once()


@pytest.mark.asyncio(loop_scope="session")
async def test_verify_email_invalid_token(client: AsyncClient):
    """Test email verification with invalid token."""
    res = await client.post(
        "/auth/verify-email",
        json={
            "token": "invalid_email_verification_token_that_is_long_enough",
        },
    )

    assert res.status_code == 400
    res_json = res.json()
    assert not res_json["success"]
    assert "invalid or expired token" in res_json["error"]["message"].lower()


@pytest.mark.asyncio(loop_scope="session")
async def test_verify_email_flow_success(client: AsyncClient):
    """Test complete email verification flow."""
    captured_token = None

    async def capture_token(to: str, token: str):
        nonlocal captured_token
        captured_token = token

    global auth_tokens

    with patch(
        "app.services.email.EmailService.send_verification_email",
        side_effect=capture_token,
    ):
        # Step 1: Request verification email
        res = await client.post(
            "/auth/send-verification-email",
            headers={"Authorization": f"Bearer {auth_tokens.tokens.access_token}"},
        )
        assert res.status_code == 200
        assert captured_token is not None

    # Step 2: Verify email with captured token
    res = await client.post(
        "/auth/verify-email",
        json={"token": captured_token},
    )

    assert res.status_code == 200
    res_json = res.json()
    assert res_json["success"]
    assert "email verified successfully" in res_json["data"]["message"].lower()


@pytest.mark.asyncio(loop_scope="session")
async def test_send_verification_email_already_verified(client: AsyncClient):
    """Test that sending verification email when already verified returns appropriate message."""
    global auth_tokens

    with patch(
        "app.services.email.EmailService.send_verification_email",
        new_callable=AsyncMock,
    ) as mock_send:
        res = await client.post(
            "/auth/send-verification-email",
            headers={"Authorization": f"Bearer {auth_tokens.tokens.access_token}"},
        )

        assert res.status_code == 200
        res_json = res.json()
        assert res_json["success"]
        assert "already verified" in res_json["data"]["message"].lower()

        # Email should NOT be sent if already verified
        mock_send.assert_not_called()


@pytest.mark.asyncio(loop_scope="session")
async def test_verify_email_token_single_use(client: AsyncClient):
    """Test that email verification tokens can only be used once."""
    # Create a new unverified user for this test
    new_user = {
        "name": "SingleUseTest",
        "email": "singleuse@test.com",
        "password": "Pass!123",
    }

    res = await client.post(
        "/auth/signup",
        json=SignupRequest(**new_user).model_dump(),
    )
    assert res.status_code == 200
    new_tokens = AuthResponse(**res.json()["data"])

    captured_token = None

    async def capture_token(to: str, token: str):
        nonlocal captured_token
        captured_token = token

    with patch(
        "app.services.email.EmailService.send_verification_email",
        side_effect=capture_token,
    ):
        res = await client.post(
            "/auth/send-verification-email",
            headers={"Authorization": f"Bearer {new_tokens.tokens.access_token}"},
        )
        assert res.status_code == 200
        assert captured_token is not None

    # First use should succeed
    res = await client.post(
        "/auth/verify-email",
        json={"token": captured_token},
    )
    assert res.status_code == 200

    # Second use should fail (token already consumed)
    res = await client.post(
        "/auth/verify-email",
        json={"token": captured_token},
    )
    assert res.status_code == 400
    assert "invalid or expired token" in res.json()["error"]["message"].lower()


# ============================================================================
# Validation Tests
# ============================================================================


@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_weak_password(client: AsyncClient):
    """Test reset password rejects weak passwords."""
    res = await client.post(
        "/auth/reset-password",
        json={
            "token": "valid_looking_token_that_is_long_enough_here",
            "password": "weak",  # Too short, no special chars
        },
    )

    assert res.status_code == 422  # Validation error
    res_json = res.json()
    assert not res_json["success"]


@pytest.mark.asyncio(loop_scope="session")
async def test_forget_password_invalid_email(client: AsyncClient):
    """Test forget password with invalid email format."""
    res = await client.post(
        "/auth/forget-password",
        json={"email": "not-an-email"},
    )

    assert res.status_code == 422  # Validation error
    res_json = res.json()
    assert not res_json["success"]
