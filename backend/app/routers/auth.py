from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import (
    RegisterRequest, SellerRegister, LoginRequest,
    TokenResponse, UserResponse, VerifyEmailRequest, ResendOtpRequest,
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    auth_service = AuthService()
    result, error = auth_service.register(
        name=data.name,
        email=data.email,
        password=data.password,
        role=data.role,
        company_name=data.company_name,
        description=data.description,
        phone=data.phone,
        address=data.address,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)

    user = result["user"]
    seller = result.get("seller")
    response = {
        "message": "Registration successful. Check your email for a verification code.",
        "email": user["email"],
        "email_status": result.get("email_status"),
        "user": UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            email_verified=user["email_verified"],
        ).model_dump(),
    }
    if seller:
        response["seller"] = {
            "id": str(seller["_id"]),
            "company_name": seller["company_name"],
            "is_approved": seller["is_approved"],
        }
    return response


@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest):
    auth_service = AuthService()
    result, error = auth_service.verify_email(data.email, data.otp)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return TokenResponse(**result)


@router.post("/resend-otp")
def resend_otp(data: ResendOtpRequest):
    auth_service = AuthService()
    _, error = auth_service.resend_otp(data.email)
    if error:
        code = status.HTTP_429_TOO_MANY_REQUESTS if "wait" in error or "Too many" in error else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=error)
    return {"message": "If the email exists, a new verification code has been sent."}


@router.post("/seller/register", status_code=status.HTTP_201_CREATED)
def register_seller(data: SellerRegister):
    auth_service = AuthService()
    result, error = auth_service.register(
        name=data.name,
        email=data.email,
        password=data.password,
        role="seller",
        company_name=data.company_name,
        description=data.description,
        phone=data.phone,
        address=data.address,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)

    user = result["user"]
    seller = result["seller"]
    return {
        "message": "Registration successful. Check your email for a verification code.",
        "email": user["email"],
        "email_status": result.get("email_status"),
        "user": UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            role=user["role"],
            is_active=user["is_active"],
            email_verified=user["email_verified"],
        ).model_dump(),
        "seller": {
            "id": str(seller["_id"]),
            "company_name": seller["company_name"],
            "is_approved": seller["is_approved"],
        },
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    auth_service = AuthService()
    result, error = auth_service.login(email=data.email, password=data.password)
    if error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)
    return TokenResponse(**result)


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    auth_service = AuthService()
    user = auth_service.get_current_user(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(**user)
