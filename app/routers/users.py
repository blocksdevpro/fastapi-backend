# app/routers/users.py

from uuid import UUID
from typing import List
from fastapi.routing import APIRouter
from app.schemas.user import (
    UserResponse,
    UserCreate
)
from app.dependencies import UserServiceDependency

from app.schemas.response import APIResponse
from app.handlers.response import response_handler

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("", response_model=APIResponse[List[UserResponse]])
@response_handler()
async def get_users(auth_service: UserServiceDependency):
    return await auth_service.get_users()

@router.post("", response_model=APIResponse[UserResponse])
@response_handler()
async def create_user(auth_service: UserServiceDependency, payload: UserCreate):
    return await auth_service.create_user(payload)

@router.get("/{user_id}", response_model=APIResponse[UserResponse])
@response_handler()
async def get_user(auth_service: UserServiceDependency, user_id: UUID):
    return await auth_service.get_user(user_id)