from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class CategoryStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    is_active: bool = True


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
