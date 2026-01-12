from app.schemas.common import QueryParams
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Annotated, Literal


NameField = Annotated[
    str, Field(..., min_length=3, max_length=25, examples=["RTX 5070TI"])
]
DescriptionField = Annotated[
    str,
    Field(
        ...,
        min_length=20,
        max_length=150,
        examples=[
            "High-performance GPU with 16GB GDDR7 memory, perfect for 4K gaming and content creation"
        ],
    ),
]

PriceField = Annotated[float, Field(..., ge=1, le=100_000, examples=[799])]
StockField = Annotated[int, Field(..., ge=0, le=100, examples=[5])]


class ProductParams(QueryParams):
    sort_by: Annotated[
        Literal["created_at", "updated_at", "name", "price", "stock"],
        Field("created_at", description="Field to sort by"),
    ]


class CreateProductRequest(BaseModel):
    name: NameField
    description: DescriptionField
    price: PriceField
    stock: StockField


class UpdateProductRequest(BaseModel):
    name: Optional[NameField] = None
    description: Optional[DescriptionField] = None
    price: Optional[PriceField] = None
    stock: Optional[StockField] = None


class ProductResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    price: float
    stock: int

    created_at: datetime
    updated_at: Optional[datetime]
