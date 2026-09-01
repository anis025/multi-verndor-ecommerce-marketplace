from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ProductStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class ProductCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    price: float = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    category_id: str
    image_url: str = Field(default="", max_length=500)
    is_active: bool = True


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    seller_id: str
    category_id: str
    name: str
    description: str
    price: float
    stock: int
    image_url: str
    is_active: bool
    seller_name: Optional[str] = None
    company_name: Optional[str] = None
    category_name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PaginatedProductsResponse(BaseModel):
    items: list
    page: int
    limit: int
    total: int
    total_pages: int
