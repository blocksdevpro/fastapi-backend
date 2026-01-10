import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio(loop_scope="session")
async def test_create_product(client: AsyncClient):
    # 1. Setup: Create and login a user to get auth headers
    user_credentials = {
        "name": "Test User",
        "email": f"test_{uuid4()}@example.com",
        "password": "Pass!123",
    }
    await client.post("/auth/signup", json=user_credentials)
    login_res = await client.post(
        "/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    access_token = login_res.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Test Create Product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product description with enough length.",
        "price": 100.0,
        "stock": 10,
    }
    res = await client.post("/products", json=product_data, headers=headers)

    assert res.status_code == 200
    res_json = res.json()
    assert res_json["success"] is True
    assert res_json["data"]["name"] == product_data["name"]
    assert res_json["data"]["id"] is not None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_products(client: AsyncClient):
    # Setup
    user_credentials = {
        "name": "Test User",
        "email": f"test_{uuid4()}@example.com",
        "password": "Pass!123",
    }
    await client.post("/auth/signup", json=user_credentials)
    login_res = await client.post(
        "/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    access_token = login_res.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a product first
    product_data = {
        "name": "Test Product",
        "description": "This is a test product description with enough length.",
        "price": 100.0,
        "stock": 10,
    }
    await client.post("/products", json=product_data, headers=headers)

    # Test Get All Products
    res = await client.get("/products", headers=headers)
    assert res.status_code == 200
    res_json = res.json()
    assert res_json["success"] is True
    assert len(res_json["data"]) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_product_by_id(client: AsyncClient):
    # Setup
    user_credentials = {
        "name": "Test User",
        "email": f"test_{uuid4()}@example.com",
        "password": "Pass!123",
    }
    await client.post("/auth/signup", json=user_credentials)
    login_res = await client.post(
        "/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    access_token = login_res.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product description with enough length.",
        "price": 100.0,
        "stock": 10,
    }
    create_res = await client.post("/products", json=product_data, headers=headers)
    product_id = create_res.json()["data"]["id"]

    # Test Get Product by ID
    res = await client.get(f"/products/{product_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["id"] == product_id

    # Test Get Non-existent Product
    res = await client.get(f"/products/{uuid4()}", headers=headers)
    assert res.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_update_product(client: AsyncClient):
    # Setup
    user_credentials = {
        "name": "Test User",
        "email": f"test_{uuid4()}@example.com",
        "password": "Pass!123",
    }
    await client.post("/auth/signup", json=user_credentials)
    login_res = await client.post(
        "/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    access_token = login_res.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product description with enough length.",
        "price": 100.0,
        "stock": 10,
    }
    create_res = await client.post("/products", json=product_data, headers=headers)
    product_id = create_res.json()["data"]["id"]

    # Test Update Product
    update_data = {"name": "Updated Name"}
    res = await client.put(f"/products/{product_id}", json=update_data, headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Updated Name"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_product(client: AsyncClient):
    # Setup
    user_credentials = {
        "name": "Test User",
        "email": f"test_{uuid4()}@example.com",
        "password": "Pass!123",
    }
    await client.post("/auth/signup", json=user_credentials)
    login_res = await client.post(
        "/auth/login",
        json={
            "email": user_credentials["email"],
            "password": user_credentials["password"],
        },
    )
    access_token = login_res.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product description with enough length.",
        "price": 100.0,
        "stock": 10,
    }
    create_res = await client.post("/products", json=product_data, headers=headers)
    product_id = create_res.json()["data"]["id"]

    # Test Delete Product
    res = await client.delete(f"/products?product_ids={product_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Verify deletion
    verify_res = await client.get(f"/products/{product_id}", headers=headers)
    assert verify_res.status_code == 404
