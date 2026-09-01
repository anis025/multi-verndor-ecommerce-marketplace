from pydantic import BaseModel, Field
from typing import Optional


class AddToCartRequest(BaseModel):
    product_id: str
    quantity: int = Field(default=1, gt=0)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    product_id: str
    seller_id: str
    product_name: str
    price: float
    quantity: int
    stock: int
    image_url: str
    subtotal: float


class CartResponse(BaseModel):
    id: str
    user_id: str
    items: list[CartItemResponse]
    total: float
    item_count: int
