from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.management import (
    UserStatusUpdateRequest,
    SellerStatusUpdateRequest,
    PasswordResetRequest,
    RoleUpdateRequest,
)
from app.services.user_service import UserService
from app.services.seller_service import SellerService
from app.services.admin_auth_service import generate_random_password
from app.core.dependencies import require_admin
from app.core.audit import log_admin_action
from app.utils.helpers import to_object_id

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: str = Query(None),
    current_user: dict = Depends(require_admin),
):
    user_service = UserService()
    is_active = None
    if role == "active":
        is_active = True
        role = None
    elif role == "inactive":
        is_active = False
        role = None

    result = user_service.get_users_paginated(page=page, limit=limit, role=role, is_active=is_active)
    return result


@router.get("/users/{user_id}")
def get_user(user_id: str, current_user: dict = Depends(require_admin)):
    to_object_id(user_id)
    user_service = UserService()
    detail = user_service.get_user_admin_detail(user_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return detail


@router.patch("/users/{user_id}/status")
def update_user_status(user_id: str, data: UserStatusUpdateRequest, current_user: dict = Depends(require_admin)):
    to_object_id(user_id)
    user_service = UserService()
    user, error = user_service.update_user_status(user_id, data.is_active)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    log_admin_action(
        current_user["user_id"], "user.status_update", "user",
        target_id=user_id, details={"is_active": data.is_active},
    )
    return user


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: str,
    data: PasswordResetRequest,
    current_user: dict = Depends(require_admin),
):
    to_object_id(user_id)
    user_service = UserService()
    new_password = data.new_password or generate_random_password()
    _, error = user_service.reset_password(user_id, new_password)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    log_admin_action(
        current_user["user_id"], "user.password_reset", "user", target_id=user_id,
    )
    return {
        "message": "Password has been reset successfully.",
        "new_password": new_password,
    }


@router.post("/users/{user_id}/verify-email")
def verify_user_email(user_id: str, current_user: dict = Depends(require_admin)):
    to_object_id(user_id)
    user_service = UserService()
    user, error = user_service.mark_email_verified(user_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    log_admin_action(
        current_user["user_id"], "user.email_verify", "user", target_id=user_id,
    )
    return user


@router.post("/users/{user_id}/role")
def change_user_role(
    user_id: str,
    data: RoleUpdateRequest,
    current_user: dict = Depends(require_admin),
):
    to_object_id(user_id)
    user_service = UserService()
    user, error = user_service.change_role(user_id, data.role.value)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    log_admin_action(
        current_user["user_id"], "user.role_update", "user",
        target_id=user_id, details={"role": data.role.value},
    )
    return user


@router.get("/sellers")
def list_sellers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    search: str = Query(None),
    current_user: dict = Depends(require_admin),
):
    seller_service = SellerService()
    result = seller_service.get_sellers_paginated(page=page, limit=limit, status=status_filter, search=search)
    return result


@router.get("/sellers/{seller_id}")
def get_seller(seller_id: str, current_user: dict = Depends(require_admin)):
    to_object_id(seller_id)
    seller_service = SellerService()
    seller = seller_service.get_seller_admin(seller_id)
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    return seller


@router.patch("/sellers/{seller_id}/status")
def update_seller_status(seller_id: str, data: SellerStatusUpdateRequest, current_user: dict = Depends(require_admin)):
    to_object_id(seller_id)
    seller_service = SellerService()
    status_value = data.status.value
    seller, error = seller_service.update_seller_status(
        seller_id=seller_id,
        status=status_value,
        reviewed_by=current_user["user_id"],
        reason=data.reason,
        notes=data.notes,
    )
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    log_admin_action(
        current_user["user_id"], f"seller.{status_value}", "seller",
        target_id=seller_id, details={"status": status_value, "reason": data.reason},
    )
    return seller
