from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.audit import log_admin_action
from app.core.dependencies import get_current_user
from app.schemas.admin import AdminLoginRequest, AdminTokenResponse, AdminVerifyOtpRequest
from app.services.admin_auth_service import AdminAuthService


router = APIRouter(prefix="/api/admin/auth", tags=["Admin Auth"])


@router.post("/login")
def request_admin_otp(data: AdminLoginRequest, request: Request):
    """Step 1: request a one-time sign-in code.

    Returns:
      * 200 + generic success — when the email is the configured admin
        address (regardless of whether an email is actually sent; the
        message is identical to avoid leaking account state).
      * 401 + "Invalid email or password." — when the email is anything
        other than the single configured admin address, or no such admin
        account exists.
    """
    ip = request.client.host if request.client else "unknown"
    service = AdminAuthService()
    ok, error, payload = service.request_login_otp(data.email, ip=ip)

    if not ok:
        log_admin_action(
            admin_id=None,
            action="admin.login_rejected",
            target_type="admin_auth",
            details={"email": (data.email or "").lower(), "ip": ip, "reason": error},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error)

    log_admin_action(
        admin_id=None,
        action="admin.login_otp_requested",
        target_type="admin_auth",
        details={"email": (data.email or "").lower(), "ip": ip},
    )
    return payload


@router.post("/verify-otp", response_model=AdminTokenResponse)
def verify_admin_otp(data: AdminVerifyOtpRequest, request: Request):
    """Step 2: verify the code and issue an admin JWT.

    Returns:
      * 200 + AdminTokenResponse on success.
      * 401 + "Invalid email or password." for non-allowlisted emails
        (or missing/non-admin accounts).
      * 429 + "Too many attempts..." when the account is currently locked.
    """
    ip = request.client.host if request.client else "unknown"
    service = AdminAuthService()
    ok, error_code, error_detail, token = service.verify_login_otp(
        data.email, data.otp, ip=ip
    )

    if not ok:
        log_admin_action(
            admin_id=None,
            action="admin.login_otp_failed",
            target_type="admin_auth",
            details={
                "email": (data.email or "").lower(),
                "ip": ip,
                "code": error_code,
                "reason": error_detail,
            },
        )
        if error_code == "locked":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=error_detail
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=error_detail
        )

    log_admin_action(
        admin_id=token["user_id"],
        action="admin.login_success",
        target_type="admin_auth",
        details={"ip": ip},
    )
    return AdminTokenResponse(**token)


@router.post("/logout")
def admin_logout(current_user: dict = Depends(get_current_user)):
    log_admin_action(
        current_user["user_id"],
        "admin.logout",
        target_type="admin_auth",
    )
    return {"message": "Logged out"}
