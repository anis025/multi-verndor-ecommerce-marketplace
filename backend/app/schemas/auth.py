from typing import Literal, Optional

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: Literal["customer", "seller"] = "customer"
    company_name: Optional[str] = Field(default=None, max_length=200)
    description: str = Field(default="", max_length=500)
    phone: str = Field(default="", max_length=20)
    address: str = Field(default="", max_length=300)

    @model_validator(mode="after")
    def _validate_role_fields(self):
        if self.role == "seller" and not self.company_name:
            raise ValueError("company_name is required when registering as a seller")
        return self


class SellerRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    company_name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(default="", max_length=500)
    phone: str = Field(default="", max_length=20)
    address: str = Field(default="", max_length=300)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendOtpRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    user: Optional[dict] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    email_verified: bool = False


class SellerResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    description: str
    phone: str
    address: str
    is_approved: bool
