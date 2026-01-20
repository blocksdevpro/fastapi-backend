from app.core.messages import ErrorMessages
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            ErrorMessages.UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
