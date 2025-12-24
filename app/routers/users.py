# app/routers/users.py


from app.utils.router import AutoAPIResponseRouter


router = AutoAPIResponseRouter(
    prefix="/users",
    tags=["users"],
)


# @router.get("", response_model=APIResponse[List[UserResponse]])
# async def get_users(user_service: UserServiceDependency):
#     return await user_service.get_users()


# @router.post("", response_model=APIResponse[UserResponse])
# @response_handler()
# async def create_user(user_service: UserServiceDependency, payload: UserCreate):
#     return await user_service.create_user(payload)


# @router.get("/{user_id}", response_model=APIResponse[UserResponse])
# @response_handler()
# async def get_user(user_service: UserServiceDependency, user_id: UUID):
#     return await user_service.get_user(user_id)
