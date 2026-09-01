from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    customer = "customer"
    seller = "seller"
    admin = "admin"


class SellerStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    suspended = "suspended"


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class PasswordResetRequest(BaseModel):
    new_password: Optional[str] = Field(default=None, min_length=6, max_length=128)


class RoleUpdateRequest(BaseModel):
    role: UserRole


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


class SellerUpdateRequest(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=300)


class SellerStatusUpdateRequest(BaseModel):
    status: SellerStatus
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class UserAdminResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SellerAdminResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    description: str
    phone: str
    address: str
    status: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    suspension_reason: Optional[str] = None
    admin_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PaginatedUsersResponse(BaseModel):
    items: list
    page: int
    limit: int
    total: int


class PaginatedSellersResponse(BaseModel):
    items: list
    page: int
    limit: int
    total: int


class SystemConfigUpdateRequest(BaseModel):
    site_name: Optional[str] = Field(None, max_length=100)
    maintenance_mode: Optional[bool] = None
    registration_open: Optional[bool] = None
    commission_rate: Optional[float] = Field(None, ge=0, le=1)
    default_page_size: Optional[int] = Field(None, ge=1, le=100)
    featured_category_ids: Optional[list] = None
    support_email: Optional[str] = Field(None, max_length=200)
    currency: Optional[str] = Field(None, max_length=10)


class SystemConfigResponse(BaseModel):
    site_name: str
    maintenance_mode: bool
    registration_open: bool
    commission_rate: float
    default_page_size: int
    featured_category_ids: list
    support_email: str
    currency: str
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: str
    admin_id: str
    action: str
    target_type: str
    target_id: Optional[str] = None
    details: dict
    created_at: str
