#!/usr/bin/env python3
"""Diagnose email/OTP sending using the app's real configuration.

Usage (from the backend/ directory):
    python scripts/test_email.py you@example.com

It prints the loaded SMTP settings (masked) and attempts to send a test
verification email through EmailService, surfacing the exact SMTP error
or confirming delivery. This isolates credential/network problems from
application logic.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.services.email_service import EmailService, validate_email_config


def mask(value: str) -> str:
    if not value:
        return "<empty>"
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def main():
    print("=== Loaded email configuration ===")
    print(f"APP_ENV      : {settings.APP_ENV}")
    print(f"SMTP_HOST    : {settings.SMTP_HOST}")
    print(f"SMTP_PORT    : {settings.SMTP_PORT}")
    print(f"SMTP_USE_SSL : {settings.SMTP_USE_SSL}")
    print(f"SMTP_USERNAME: {mask(settings.SMTP_USERNAME)}")
    print(f"SMTP_PASSWORD: {mask(settings.SMTP_PASSWORD)}")
    print(f"EMAIL_FROM   : {settings.EMAIL_FROM or '<empty>'}")

    if settings.APP_ENV == "production":
        try:
            validate_email_config()
            print("validate_email_config: OK")
        except RuntimeError as e:
            print(f"validate_email_config: FAILED -> {e}")
            return

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print(
            "\n[email:skip] SMTP credentials are empty in the RUNNING process.\n"
            "Fix: ensure backend/.env has SMTP_USERNAME/SMTP_PASSWORD (and EMAIL_FROM),\n"
            "and that the server was (re)started from the backend/ directory so .env is loaded.\n"
            "Under Docker, the compose file must pass these (env_file / SMTP_* environment)."
        )
        return

    target = sys.argv[1] if len(sys.argv) > 1 else settings.ADMIN_EMAIL
    print(f"\n=== Sending test verification email to {target} ===")
    try:
        ok = EmailService().send_verification_email(target, "123456")
        if ok:
            print("[email:sent] SUCCESS - check the inbox (and Spam) for the test code 123456.")
        else:
            print("[email:error] send returned False - see server log line above for the reason.")
    except Exception as e:  # pragma: no cover - defensive
        print(f"[email:error] {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
