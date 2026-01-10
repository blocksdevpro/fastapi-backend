from pydantic import BaseModel, Field
from typing import Literal, Optional, Annotated


class QueryParams(BaseModel):
    query: Annotated[Optional[str], Field("", description="Search query")]
    page: Annotated[int, Field(1, ge=1, description="Page number")]
    limit: Annotated[
        int, Field(10, ge=1, le=100, description="Number of items per page")
    ]

    sort_by: Annotated[
        Literal["created_at", "updated_at", "name", "price"],
        Field("created_at", description="Field to sort by"),
    ]
    sort_order: Annotated[
        Literal["asc", "desc"], Field("desc", description="Sort order")
    ]

    @property
    def offset(self):
        return (self.page - 1) * self.limit
