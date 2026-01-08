import pytest
from httpx import AsyncClient, Response

from app.schemas.auth import AuthResponse, SignupRequest, LoginRequest


user_credentials = {"name": "Uttam", "email": "mail@uttam.com", "password": "Pass!123"}

auth_tokens: AuthResponse


@pytest.mark.asyncio(loop_scope="session")
async def test_health(client: AsyncClient):
    res = await client.get("/health")
    assert res.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_success_signup(client: AsyncClient):
    res: Response = await client.post(
        "/auth/signup",
        json=SignupRequest(**user_credentials).model_dump(),
    )
    assert res.status_code == 200
    assert res.json() != {}

    global auth_tokens
    auth_tokens = AuthResponse(**res.json()["data"])


@pytest.mark.asyncio(loop_scope="session")
async def test_failed_signup(client: AsyncClient):
    res: Response = await client.post(
        "/auth/signup",
        json=SignupRequest(**user_credentials).model_dump(),
    )
    assert res.status_code == 400
    res_json = res.json()
    assert res_json != {}
    assert not res_json["success"]
    assert res_json["error"]["message"] == "User already exists"


@pytest.mark.asyncio(loop_scope="session")
async def test_success_login(client: AsyncClient):
    res = await client.post(
        "/auth/login", json=LoginRequest(**user_credentials).model_dump()
    )
    assert res.status_code == 200
    assert res.json() != {}

    global auth_tokens
    auth_tokens = AuthResponse(**res.json()["data"])


@pytest.mark.asyncio(loop_scope="session")
async def test_failed_login(client: AsyncClient):
    res = await client.post(
        "/auth/login",
        json={"email": user_credentials["email"], "password": "123"},
    )
    assert res.status_code == 422
    res_json = res.json()

    assert res_json != {}
    assert not res_json["success"]
    assert res_json["error"]["message"] == "Validation Error"


@pytest.mark.asyncio(loop_scope="session")
async def test_success_access_token(client: AsyncClient):
    global auth_tokens
    res = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {auth_tokens.tokens.access_token}"},
    )
    assert res.status_code == 200
    res_json = res.json()

    assert res_json != {}
    assert res_json["success"]
    assert res_json["data"]["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_success_refresh_token(client: AsyncClient):
    global auth_tokens
    res = await client.post(
        "/auth/refresh",
        json={"refresh_token": auth_tokens.tokens.refresh_token},
    )
    assert res.status_code == 200
    res_json = res.json()

    assert res_json != {}
    assert res_json["success"]
    assert res_json["data"]["tokens"]

    auth_tokens.tokens.access_token = res_json["data"]["tokens"]["access_token"]


@pytest.mark.asyncio(loop_scope="session")
async def test_success_logout_token(client: AsyncClient):
    global auth_tokens
    res = await client.post(
        "/auth/logout",
        json={"refresh_token": auth_tokens.tokens.refresh_token},
        headers={"Authorization": f"Bearer {auth_tokens.tokens.access_token}"},
    )
    assert res.status_code == 200
    res_json = res.json()

    assert res_json != {}
    assert res_json["success"]
    assert res_json["data"]["message"]


@pytest.mark.asyncio(loop_scope="session")
async def test_failed_refresh_token(client: AsyncClient):
    global auth_tokens
    res = await client.post(
        "/auth/refresh",
        json={"refresh_token": auth_tokens.tokens.refresh_token},
    )
    assert res.status_code == 401
    res_json = res.json()

    assert res_json != {}
    assert not res_json["success"]
