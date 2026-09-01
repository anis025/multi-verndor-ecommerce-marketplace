"""Tests for the passwordless admin login (email OTP, single allowed email).

Contract:
  * Only ADMIN_ALLOWED_EMAIL can authenticate.
  * Any other email returns 401 "Invalid credentials." on BOTH
    the request and verify endpoints.
  * The allowlisted email returns 200 + generic success; the code is sent.
"""
from datetime import datetime, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import hash_password


def _seed_admin(db, email="mdanis.dev@gmail.com", is_active=True, name="Admin"):
    db.users.delete_many({"email": email})
    db.users.insert_one({
        "name": name,
        "email": email,
        "password_hash": hash_password("unused"),
        "role": "admin",
        "is_active": is_active,
        "email_verified": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })


class TestRequestAdminOtp:
    def test_request_allowed_email_sends_code(self, client, db, otp_sink, monkeypatch):
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        _seed_admin(db)
        resp = client.post("/api/admin/auth/login", json={"email": "mdanis.dev@gmail.com"})
        assert resp.status_code == 200
        assert "verification code" in resp.json()["message"]
        assert "mdanis.dev@gmail.com" in otp_sink
        assert len(otp_sink["mdanis.dev@gmail.com"]) == 6

    def test_request_non_allowed_email_returns_401(self, client, db, otp_sink):
        # An admin account under a different email must still be blocked
        # from the admin login endpoint because of the allowed-email gate.
        _seed_admin(db, email="other-admin@example.com", name="Other")
        resp = client.post("/api/admin/auth/login", json={"email": "other-admin@example.com"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials."
        # No email should be sent.
        assert otp_sink == {}

    def test_request_unknown_email_returns_401(self, client, db, otp_sink):
        resp = client.post("/api/admin/auth/login", json={"email": "nobody@example.com"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials."
        assert otp_sink == {}

    def test_request_deactivated_admin_returns_401(self, client, db, otp_sink, monkeypatch):
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        _seed_admin(db, is_active=False)
        resp = client.post("/api/admin/auth/login", json={"email": "mdanis.dev@gmail.com"})
        # Allowlist passes, but the account is inactive -> 401.
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials."
        assert otp_sink == {}

    def test_request_resend_cooldown(self, client, db, otp_sink, monkeypatch):
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        _seed_admin(db)
        client.post("/api/admin/auth/login", json={"email": "mdanis.dev@gmail.com"})
        first = otp_sink["mdanis.dev@gmail.com"]
        # Immediate second request should NOT issue a new code (60s cooldown).
        client.post("/api/admin/auth/login", json={"email": "mdanis.dev@gmail.com"})
        assert otp_sink["mdanis.dev@gmail.com"] == first


class TestVerifyAdminOtp:
    def _seed_and_request(self, client, db, otp_sink, monkeypatch):
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        _seed_admin(db)
        client.post("/api/admin/auth/login", json={"email": "mdanis.dev@gmail.com"})
        return otp_sink["mdanis.dev@gmail.com"]

    def test_verify_success_returns_token(self, client, db, otp_sink, monkeypatch):
        otp = self._seed_and_request(client, db, otp_sink, monkeypatch)
        resp = client.post(
            "/api/admin/auth/verify-otp",
            json={"email": "mdanis.dev@gmail.com", "otp": otp},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        payload = jwt.decode(
            data["access_token"], settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        assert payload["role"] == "admin"
        assert payload["sub"] == data["user_id"]

    def test_verify_wrong_otp(self, client, db, otp_sink, monkeypatch):
        self._seed_and_request(client, db, otp_sink, monkeypatch)
        resp = client.post(
            "/api/admin/auth/verify-otp",
            json={"email": "mdanis.dev@gmail.com", "otp": "000000"},
        )
        assert resp.status_code == 401
        assert "Invalid" in resp.json()["detail"]

    def test_verify_unknown_email_returns_401(self, client):
        resp = client.post(
            "/api/admin/auth/verify-otp",
            json={"email": "nobody@example.com", "otp": "123456"},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials."

    def test_verify_non_allowed_email_returns_401(self, client, db, otp_sink, monkeypatch):
        # Even if a separate admin account exists under a different email,
        # the verify endpoint rejects it because of the allowlist gate.
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        _seed_admin(db, email="other-admin@example.com")
        resp = client.post(
            "/api/admin/auth/verify-otp",
            json={"email": "other-admin@example.com", "otp": "123456"},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials."

    def test_verify_lockout_after_5_failures(self, client, db, otp_sink, monkeypatch):
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        self._seed_and_request(client, db, otp_sink, monkeypatch)
        for _ in range(5):
            r = client.post(
                "/api/admin/auth/verify-otp",
                json={"email": "mdanis.dev@gmail.com", "otp": "000000"},
            )
            assert r.status_code == 401
        # 6th attempt is locked (429).
        locked = client.post(
            "/api/admin/auth/verify-otp",
            json={"email": "mdanis.dev@gmail.com", "otp": "000000"},
        )
        assert locked.status_code == 429
        assert "Too many" in locked.json()["detail"]

    def test_verify_does_not_reactivate_deactivated_account(self, client, db, otp_sink, monkeypatch):
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        # Seed active, request a code, then deactivate before verify.
        _seed_admin(db)
        client.post("/api/admin/auth/login", json={"email": "mdanis.dev@gmail.com"})
        otp = otp_sink["mdanis.dev@gmail.com"]
        db.users.update_one(
            {"email": "mdanis.dev@gmail.com"}, {"$set": {"is_active": False}}
        )
        resp = client.post(
            "/api/admin/auth/verify-otp",
            json={"email": "mdanis.dev@gmail.com", "otp": otp},
        )
        # Inactive account must not authenticate.
        assert resp.status_code == 401
        # Confirm is_active stayed False (no auto-reactivation).
        user = db.users.find_one({"email": "mdanis.dev@gmail.com"})
        assert user["is_active"] is False


class TestAdminLogout:
    def test_admin_logout_requires_auth(self, client):
        resp = client.post("/api/admin/auth/logout")
        assert resp.status_code in (401, 403)

    def test_admin_logout_success(self, client, db, otp_sink, monkeypatch):
        from app.services import email_service as email_service_mod
        monkeypatch.setattr(
            email_service_mod.EmailService,
            "send_admin_login_otp",
            lambda self, to, otp: otp_sink.update({to: otp}) or True,
        )
        _seed_admin(db)
        client.post("/api/admin/auth/login", json={"email": "mdanis.dev@gmail.com"})
        otp = otp_sink["mdanis.dev@gmail.com"]
        v = client.post(
            "/api/admin/auth/verify-otp",
            json={"email": "mdanis.dev@gmail.com", "otp": otp},
        )
        token = v.json()["access_token"]
        resp = client.post(
            "/api/admin/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
