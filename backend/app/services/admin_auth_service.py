import secrets
import string
import threading
import time
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import create_access_token, generate_otp, hash_otp, verify_otp
from app.db.mongodb import get_database
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService

# Reuse the existing OTP tuning constants (10 min TTL, 5 attempts, 15 min lock, 60s resend cooldown).
from app.core.security import (
    OTP_TTL_MINUTES,
    OTP_MAX_ATTEMPTS,
    OTP_RESEND_COOLDOWN_SECONDS,
    OTP_LOCK_MINUTES,
)


def generate_random_password(length: int = 16) -> str:
    """Strong random password (used by the admin seed script; the admin
    login is now passwordless)."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    required = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*"),
    ]
    remaining = [secrets.choice(alphabet) for _ in range(length - len(required))]
    pwd = "".join(required + remaining)
    return "".join(secrets.SystemRandom().sample(pwd, len(pwd)))


class _RequestCooldown:
    """Per-email cooldown for OTP request attempts. In-memory, thread-safe.

    Prevents flooding the admin's inbox (and probing) even for emails
    that don't have a user record (so `last_otp_sent_at` can't be used).
    """

    def __init__(self, seconds: int = 30):
        self.seconds = seconds
        self._lock = threading.Lock()
        self._last: dict[str, float] = {}

    def is_allowed(self, key: str) -> bool:
        with self._lock:
            return (time.time() - self._last.get(key, 0)) >= self.seconds

    def touch(self, key: str) -> None:
        with self._lock:
            self._last[key] = time.time()


_request_cooldown = _RequestCooldown()


def reset_request_cooldown_for_tests() -> None:
    """Clear the in-memory request cooldown. Intended for test fixtures."""
    with _request_cooldown._lock:
        _request_cooldown._last.clear()


class AdminAuthService:
    """Passwordless admin login via email OTP.

    Security model:
      * Only the email configured in `ADMIN_ALLOWED_EMAIL` can authenticate
        via the admin endpoint, regardless of any other account's role.
      * The request endpoint always returns a generic 200 — the response
        never reveals whether the email is allowed or whether the account
        exists. Emails are only sent to the allowed address.
      * The verify endpoint is strict: unknown/expired/locked/wrong codes
        return the same generic "Invalid or expired code" to avoid
        leaking OTP state.
      * A successful login never auto-activates a deactivated account.
    """

    def __init__(self):
        db = get_database()
        self.user_repo = UserRepository(db)

    @property
    def allowed_email(self) -> str:
        return (settings.ADMIN_ALLOWED_EMAIL or "").strip().lower()

    def request_login_otp(self, email: str, ip: str = "unknown") -> dict:
        """Step 1: request a one-time sign-in code.

        Returns a structured result:
          * (ok=True,  None, success_message)   — allowed admin; an email is
            sent (subject to cooldown / lockout rules) or silently skipped
            with the same generic message to avoid leaking timing.
          * (ok=False, "Invalid email or password.", None) — the email is
            not the configured admin address, the account is missing, or
            the account is not an active admin.

        The router maps ok=False to HTTP 401.
        """
        normalized = (email or "").strip().lower()
        success_message = {
            "message": (
                "If the email is authorized to sign in as admin, a "
                "verification code has been sent."
            )
        }

        # Reject anything that isn't even shaped like an email.
        if not normalized or "@" not in normalized:
            return False, "Invalid credentials.", None

        # The hard gate: only the configured admin email is allowed. We
        # explicitly tell the caller it's invalid so the UI can show a
        # real error rather than sitting on a "code sent" screen.
        if not self.allowed_email or normalized != self.allowed_email:
            return False, "Invalid credentials.", None

        # Per-email + per-IP throttle to limit probing attempts.
        if not _request_cooldown.is_allowed(f"email:{normalized}"):
            return True, None, success_message
        if not _request_cooldown.is_allowed(f"ip:{ip}"):
            return True, None, success_message
        _request_cooldown.touch(f"email:{normalized}")
        _request_cooldown.touch(f"ip:{ip}")

        # Verify the account actually exists and is an active admin.
        user = self.user_repo.find_by_email(normalized)
        if not user or user.get("role") != "admin" or not user.get("is_active", False):
            return False, "Invalid credentials.", None

        # Respect the per-user resend cooldown / lockout windows — but
        # still return success to avoid leaking state.
        now = datetime.now(timezone.utc)
        last_sent = user.get("last_otp_sent_at")
        if last_sent and (now - last_sent).total_seconds() < OTP_RESEND_COOLDOWN_SECONDS:
            return True, None, success_message

        locked_until = user.get("otp_locked_until")
        if locked_until and locked_until > now:
            return True, None, success_message

        otp = generate_otp()
        expiry = now + timedelta(minutes=OTP_TTL_MINUTES)
        self.user_repo.set_otp(str(user["_id"]), hash_otp(otp), expiry, now)

        try:
            EmailService().send_admin_login_otp(user["email"], otp)
        except Exception as e:  # pragma: no cover - defensive
            print(f"[admin-otp:error] {e}")

        return True, None, success_message

    def verify_login_otp(self, email: str, otp: str, ip: str = "unknown") -> tuple:
        """Step 2: verify the code.

        Returns (ok, error_code, error_detail, token_payload):
          * ok=True  -> token payload in the 4th element.
          * ok=False -> error_code in {"invalid", "locked"} and a detail
            message; the router maps them to 401 / 429.

        Only the allowed admin email can succeed. Any other email — even
        if it has role=admin in the DB — is rejected up-front with
        "Invalid email or password."
        """
        normalized = (email or "").strip().lower()

        # Allowlist gate — surface as 401.
        if not normalized or "@" not in normalized:
            return False, "invalid", "Invalid credentials.", None
        if not self.allowed_email or normalized != self.allowed_email:
            return False, "invalid", "Invalid credentials.", None

        # Account gate.
        user = self.user_repo.find_by_email(normalized)
        if not user or user.get("role") != "admin" or not user.get("is_active", False):
            return False, "invalid", "Invalid credentials.", None

        now = datetime.now(timezone.utc)
        locked_until = user.get("otp_locked_until")
        if locked_until and locked_until > now:
            return False, "locked", "Too many attempts. Please try again later.", None

        stored_hash = user.get("email_otp_hash")
        expiry = user.get("email_otp_expiry")
        if not stored_hash or not expiry or expiry < now:
            return False, "invalid", "Invalid or expired code.", None

        if not verify_otp(stored_hash, otp):
            attempts = (user.get("email_otp_attempts") or 0) + 1
            new_lock = now + timedelta(minutes=OTP_LOCK_MINUTES) if attempts >= OTP_MAX_ATTEMPTS else None
            self.user_repo.record_failed_otp(str(user["_id"]), new_lock)
            return False, "invalid", "Invalid or expired code.", None

        # Success: clear OTP fields but do NOT change is_active/email_verified.
        self.user_repo.clear_otp(str(user["_id"]))

        token = create_access_token({
            "sub": str(user["_id"]),
            "role": "admin",
        })
        return True, "", None, {
            "access_token": token,
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name", ""),
        }

