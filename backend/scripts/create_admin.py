"""
Seed the marketplace admin account using the configured ADMIN_ALLOWED_EMAIL.

The admin logs in passwordlessly via email OTP (POST /api/admin/auth/login then
POST /api/admin/auth/verify-otp). The password stored on the user document is
NOT used for login — it is kept only to satisfy the user schema. A strong
random password is generated and is not displayed.

Re-running this script is safe: any existing user with the same email is
replaced.
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import hash_password
from app.db.mongodb import connect_to_mongo, get_database
from app.services.admin_auth_service import generate_random_password


def main():
    db = connect_to_mongo()
    try:
        email = (settings.ADMIN_ALLOWED_EMAIL or settings.ADMIN_EMAIL).strip().lower()
        if not email:
            print("ERROR: ADMIN_ALLOWED_EMAIL is not set in backend/.env")
            sys.exit(1)

        if email != (settings.ADMIN_ALLOWED_EMAIL or "").strip().lower():
            print(
                f"WARNING: ADMIN_ALLOWED_EMAIL is not set; falling back to ADMIN_EMAIL={email}"
            )

        # Remove any existing user with this email (idempotent reseed).
        db.users.delete_many({"email": email})

        password = generate_random_password()
        now = datetime.now(timezone.utc)
        db.users.insert_one({
            "name": settings.ADMIN_NAME,
            "email": email,
            "password_hash": hash_password(password),
            "role": "admin",
            "is_active": True,
            "email_verified": True,
            "created_at": now,
            "updated_at": now,
        })

        print("=" * 56)
        print("Admin account ready.")
        print(f"  Email      : {email}")
        print("  Login      : /admin/login  (passwordless email OTP)")
        print(f"  Brand      : {settings.BRAND_NAME}")
        print("=" * 56)
        print("A one-time sign-in code will be emailed on each login attempt.")
        print("Only this email is allowed to log in as admin.")
    finally:
        # Keep the connection short-lived for the script.
        from app.db.mongodb import close_mongo_connection
        close_mongo_connection()


if __name__ == "__main__":
    main()
