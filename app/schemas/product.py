from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Annotated


class CreateProductRequest(BaseModel):
    name: Annotated[
        str, Field(..., min_length=3, max_length=25, examples=["RTX 5070TI"])
    ]
    description: Annotated[
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
    price: Annotated[float, Field(..., ge=1, le=100_000, examples=[799])]
    stock: Annotated[int, Field(..., ge=0, le=100, examples=[5])]


class ProductResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    price: float
    stock: int

    created_at: datetime
    updated_at: Optional[datetime]
