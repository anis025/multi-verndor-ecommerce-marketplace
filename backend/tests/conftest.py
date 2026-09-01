import os

from pymongo import MongoClient

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import app.services.email_service as email_service_mod
import app.services.admin_auth_service as admin_auth_service_mod
from app.core.config import settings

# Isolate the test process from the live database. We force the test DB
# here at import time AND patch connect_to_mongo so every subsequent
# connect (including the TestClient startup, create_indexes, and any
# service that calls get_database) lands on hatify_test, never hatify_db.
os.environ["DATABASE_NAME"] = "hatify_test"
settings.DATABASE_NAME = "hatify_test"

import app.db.mongodb as mongo_mod

_original_connect_to_mongo = mongo_mod.connect_to_mongo


def _connect_to_test_db():
    if mongo_mod.client is None or mongo_mod.db is None or mongo_mod.db.name != "hatify_test":
        mongo_mod.client = MongoClient(settings.MONGODB_URL, tz_aware=True)
        mongo_mod.client.admin.command("ping")
    mongo_mod.db = mongo_mod.client["hatify_test"]
    return mongo_mod.db


mongo_mod.connect_to_mongo = _connect_to_test_db


# Disable real email sending during the test suite (SMTP creds may be live).
settings.EMAIL_ENABLED = False


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
    close_mongo_connection()


@pytest.fixture(scope="module")
def db():
    db = mongo_mod.connect_to_mongo()
    yield db
    close_mongo_connection()


@pytest.fixture(autouse=True)
def clean_db(db):
    # Clear the in-memory request cooldown so request-rate-limit tests are
    # deterministic across the module-level TestClient/db fixtures.
    admin_auth_service_mod.reset_request_cooldown_for_tests()
    yield
    db.users.delete_many({})
    db.sellers.delete_many({})
    db.products.delete_many({})
    db.categories.delete_many({})
    db.carts.delete_many({})
    db.orders.delete_many({})
    db.reviews.delete_many({})
    db.notifications.delete_many({})


@pytest.fixture
def otp_sink(monkeypatch):
    """Capture OTPs emitted by the email service during tests (no real SMTP)."""
    sink = {}

    def fake_send(self, to, otp):
        sink[to.lower()] = otp
        return True

    monkeypatch.setattr(email_service_mod.EmailService, "send_verification_email", fake_send)
    return sink


@pytest.fixture
def register_and_verify():
    """Register then verify the email using the captured OTP; returns verify response."""
    def _do(client, otp_sink, **payload):
        r = client.post("/api/auth/register", json=payload)
        assert r.status_code == 201, r.text
        email = payload["email"].lower()
        otp = otp_sink[email]
        v = client.post("/api/auth/verify-email", json={"email": email, "otp": otp})
        assert v.status_code == 200, v.text
        return v
    return _do
