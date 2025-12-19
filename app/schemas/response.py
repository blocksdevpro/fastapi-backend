# app/schemas/response.py

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    page: int
    limit: int
    total: int


class Metadata(BaseModel):
    pagination: Optional[PaginationMetadata] = None


class ErrorDetail(BaseModel):
    field: str
    message: str


class Error(BaseModel):
    code: int
    message: str
    details: Optional[List[ErrorDetail]] = None


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    meta: Optional[Metadata] = None
    error: Optional[Error] = None

    def model_dump(self, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(**kwargs)
