from httpx import AsyncClient, Response
import pytest

from app.schemas.auth import AuthResponse, SignupRequest, LoginRequest
from app.schemas.response import APIResponse


user_credentials = {"name": "Uttam", "email": "mail@uttam.com", "password": "Pass!123"}

auth_response: APIResponse[AuthResponse]


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
    global auth_response
    auth_response = APIResponse[AuthResponse](**res.json())


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

    global auth_response
    auth_response = APIResponse[AuthResponse](**res.json())


@pytest.mark.asyncio(loop_scope="session")
async def test_failed_login(client: AsyncClient):
    res = await client.post(
        "/auth/login",
        json=LoginRequest(email=user_credentials["email"], password="123").model_dump(),
    )
    assert res.status_code == 401
    res_json = res.json()

    assert res_json != {}
    assert not res_json["success"]
    assert res_json["error"]["message"] == "Invalid credentials"
