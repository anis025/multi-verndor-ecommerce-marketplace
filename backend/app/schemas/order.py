from pydantic import BaseModel, Field
from typing import Optional


class ShippingAddress(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    address: str = Field(..., min_length=1, max_length=500)


class CreateOrderRequest(BaseModel):
    shipping_address: ShippingAddress


class OrderItemResponse(BaseModel):
    product_id: str
    seller_id: str
    seller_name: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float
    seller_status: str


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    items: list[OrderItemResponse]
    total_amount: float
    shipping_address: dict
    status: str
    created_at: str
    updated_at: str


class PaginatedOrdersResponse(BaseModel):
    items: list
    page: int
    limit: int
    total: int
    total_pages: int
