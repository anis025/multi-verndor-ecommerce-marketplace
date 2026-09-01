from datetime import datetime, timedelta, timezone

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_otp,
    hash_otp,
    verify_otp,
    OTP_TTL_MINUTES,
    OTP_MAX_ATTEMPTS,
    OTP_RESEND_COOLDOWN_SECONDS,
    OTP_LOCK_MINUTES,
)
from app.db.mongodb import get_database
from app.repositories.user_repository import UserRepository
from app.repositories.seller_repository import SellerRepository
from app.services.email_service import EmailService


class AuthService:
    def __init__(self):
        db = get_database()
        self.user_repo = UserRepository(db)
        self.seller_repo = SellerRepository(db)

    def register(self, name: str, email: str, password: str, role: str = "customer",
                  company_name: str = None, description: str = "", phone: str = "", address: str = ""):
        if self.user_repo.email_exists(email):
            return None, "Email already registered"

        now = datetime.now(timezone.utc)
        user_data = {
            "name": name,
            "email": email.lower(),
            "password_hash": hash_password(password),
            "role": role,
            "is_active": False,
            "email_verified": False,
            "created_at": now,
            "updated_at": now,
        }
        user = self.user_repo.create(user_data)

        seller = None
        if role == "seller":
            seller_data = {
                "user_id": user["_id"],
                "company_name": company_name or name,
                "description": description,
                "phone": phone,
                "address": address,
                "is_approved": False,
                "status": "pending",
                "created_at": now,
                "updated_at": now,
            }
            seller = self.seller_repo.create(seller_data)

        email_status = self._send_otp(user)

        return {"user": user, "seller": seller, "email_status": email_status}, None

    def _send_otp(self, user: dict) -> str:
        """Generate, store (hashed), and email a verification OTP.

        Email failures are swallowed so a successful registration is never
        blocked by SMTP issues (per SKILLS.md email-failure handling).
        Returns a status string: "sent", "not_sent", or "error".
        """
        otp = generate_otp()
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(minutes=OTP_TTL_MINUTES)
        try:
            self.user_repo.set_otp(str(user["_id"]), hash_otp(otp), expiry, now)
            sent = EmailService().send_verification_email(user["email"], otp)
            status = "sent" if sent else "not_sent"
            print(f"[otp] verification email for {user['email']}: {status}")
            return status
        except Exception as e:
            print(f"[otp:error] failed to send verification email to {user['email']}: {e}")
            return "error"

    def verify_email(self, email: str, otp: str):
        user = self.user_repo.find_by_email(email)
        if not user:
            return None, "Invalid or expired verification code"

        if user.get("email_verified"):
            return None, "Email already verified. Please login."

        now = datetime.now(timezone.utc)
        locked_until = user.get("otp_locked_until")
        if locked_until and locked_until > now:
            return None, "Too many attempts. Please try again later."

        stored_hash = user.get("email_otp_hash")
        expiry = user.get("email_otp_expiry")
        if not stored_hash or not expiry or expiry < now:
            return None, "Invalid or expired verification code"

        if not verify_otp(stored_hash, otp):
            attempts = user.get("email_otp_attempts", 0) + 1
            new_lock = None
            if attempts >= OTP_MAX_ATTEMPTS:
                new_lock = now + timedelta(minutes=OTP_LOCK_MINUTES)
            self.user_repo.record_failed_otp(str(user["_id"]), new_lock)
            if new_lock:
                return None, "Too many attempts. Please try again later."
            return None, "Invalid or expired verification code"

        self.user_repo.mark_verified(str(user["_id"]))
        token = create_access_token({
            "sub": str(user["_id"]),
            "role": user["role"],
        })
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user["role"],
            "user_id": str(user["_id"]),
            "user": self.get_current_user(str(user["_id"])),
        }, None

    def resend_otp(self, email: str):
        user = self.user_repo.find_by_email(email)
        if not user:
            # Silent success to avoid email enumeration.
            return {}, None
        if user.get("email_verified"):
            return None, "Email already verified. Please login."

        now = datetime.now(timezone.utc)
        locked_until = user.get("otp_locked_until")
        if locked_until and locked_until > now:
            return None, "Too many attempts. Please try again later."

        last_sent = user.get("last_otp_sent_at")
        if last_sent and (now - last_sent).total_seconds() < OTP_RESEND_COOLDOWN_SECONDS:
            return None, "Please wait a moment before requesting a new code."

        self._send_otp(user)
        return {}, None

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.find_by_email(email)
        if not user:
            return None, "Invalid email or password"

        if not verify_password(password, user["password_hash"]):
            return None, "Invalid email or password"

        if user.get("email_verified") is False:
            return None, "Please verify your email address before logging in."

        if not user.get("is_active", False):
            return None, "Account is deactivated"

        token = create_access_token({
            "sub": str(user["_id"]),
            "role": user["role"],
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user["role"],
            "user_id": str(user["_id"]),
            "user": self.get_current_user(str(user["_id"])),
        }, None

    def get_current_user(self, user_id: str) -> dict:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None

        result = {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user.get("is_active", True),
            "email_verified": user.get("email_verified", True),
        }

        if user["role"] == "seller":
            seller = self.seller_repo.find_by_user_id(user_id)
            if seller:
                result["seller_id"] = str(seller["_id"])
                result["company_name"] = seller["company_name"]
                result["is_approved"] = seller.get("is_approved", False)

        return result
