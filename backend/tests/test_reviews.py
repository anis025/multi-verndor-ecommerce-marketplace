"""Tests for reviews and for CORS on /uploads/."""
import io
import time
from datetime import datetime, timezone

import jwt
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import hash_password
from app.main import app


def _make_token(user_id, role="customer"):
    return jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "exp": datetime.now(timezone.utc).timestamp() + 3600,
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# ---------------------------------------------------------------------------
# CORS header on /uploads
# ---------------------------------------------------------------------------

class TestUploadsCors:
    def test_uploads_response_has_cors_header(self, client):
        # Create a small image via the seller upload endpoint isn't necessary;
        # we just hit /uploads/ and check the response headers for CORS.
        # Use a known-existent file (the test suite's pre-seeded uploads dir
        # may be empty; if so, write one).
        import os
        upload_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "uploads",
        )
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, "cors_test.png")
        with open(path, "wb") as f:
            f.write(bytes.fromhex(
                "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C489"
                "0000000D4944415478DA63646060F8CF0000030100010078D3FA540000000049"
                "454E44AE426082"
            ))
        try:
            r = client.get("/uploads/cors_test.png")
            assert r.status_code == 200
            assert r.headers.get("access-control-allow-origin") is not None
            assert r.headers.get("cross-origin-resource-policy") == "cross-origin"
        finally:
            try:
                os.remove(path)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

def _seed_seller_with_product(db):
    """Create an approved seller with a product; return (seller_user_id, product_id)."""
    now = datetime.now(timezone.utc)
    db.users.delete_many({"email": "review-seller@example.com"})
    db.sellers.delete_many({"company_name": "Review Shop"})
    db.products.delete_many({"name": "Reviewable Widget"})
    seller_uid = db.users.insert_one({
        "name": "Review Seller",
        "email": "review-seller@example.com",
        "password_hash": hash_password("x"),
        "role": "seller",
        "is_active": True,
        "email_verified": True,
        "created_at": now,
        "updated_at": now,
    }).inserted_id
    seller_id = db.sellers.insert_one({
        "user_id": seller_uid,
        "company_name": "Review Shop",
        "is_approved": True,
        "status": "approved",
        "created_at": now,
        "updated_at": now,
    }).inserted_id
    product_id = db.products.insert_one({
        "name": "Reviewable Widget",
        "description": "x",
        "price": 10.0,
        "stock": 5,
        "seller_id": seller_id,
        "category_id": ObjectId(),
        "is_active": True,
        "image_url": "",
        "created_at": now,
        "updated_at": now,
    }).inserted_id
    return str(seller_uid), str(product_id)


def _seed_purchaser(db, email="reviewer@example.com", with_order=True):
    now = datetime.now(timezone.utc)
    db.users.delete_many({"email": email})
    uid = db.users.insert_one({
        "name": "Reviewer",
        "email": email,
        "password_hash": hash_password("x"),
        "role": "customer",
        "is_active": True,
        "email_verified": True,
        "created_at": now,
        "updated_at": now,
    }).inserted_id
    return str(uid)


class TestReviews:
    def test_create_review_requires_auth(self, client, db):
        _, pid = _seed_seller_with_product(db)
        r = client.post(f"/api/products/{pid}/reviews", json={"rating": 5, "title": "ok", "body": "ok"})
        assert r.status_code in (401, 403)

    def test_create_review_non_purchaser_rejected(self, client, db):
        seller_uid, pid = _seed_seller_with_product(db)
        cust_uid = _seed_purchaser(db, email="nopurchase@example.com", with_order=False)
        token = _make_token(cust_uid)
        r = client.post(
            f"/api/products/{pid}/reviews",
            json={"rating": 5, "title": "ok", "body": "ok"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 400
        assert "purchased" in r.json()["detail"].lower()

    def test_create_review_purchaser_succeeds_and_aggregates(self, client, db):
        seller_uid, pid = _seed_seller_with_product(db)
        cust_uid = _seed_purchaser(db, email="buyer@example.com", with_order=True)
        # Create a fake past order containing this product for the buyer.
        db.orders.delete_many({"customer_id": ObjectId(cust_uid)})
        db.orders.insert_one({
            "customer_id": ObjectId(cust_uid),
            "items": [{"product_id": ObjectId(pid), "seller_id": ObjectId(), "product_name": "x", "quantity": 1, "unit_price": 10, "subtotal": 10, "seller_status": "delivered"}],
            "total_amount": 10,
            "shipping_address": {"name": "x", "phone": "1", "address": "y"},
            "status": "delivered",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        token = _make_token(cust_uid)
        r = client.post(
            f"/api/products/{pid}/reviews",
            json={"rating": 5, "title": "Great", "body": "Loved it"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["rating"] == 5
        assert data["status"] == "approved"
        assert data["user_name"] == "Reviewer"

        # Duplicate review is rejected
        r2 = client.post(
            f"/api/products/{pid}/reviews",
            json={"rating": 4, "title": "ok", "body": "ok"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r2.status_code == 400

        # Product detail includes the rating
        r3 = client.get(f"/api/products/{pid}")
        assert r3.status_code == 200
        product = r3.json()
        assert product["avg_rating"] == 5.0
        assert product["review_count"] == 1
        # company_name is included on the product response
        assert product["company_name"] == "Review Shop"
        assert product["seller_name"] == "Review Seller"
        # image_url field is present (empty here)
        assert "image_url" in product

        # Reviews listing
        r4 = client.get(f"/api/products/{pid}/reviews")
        assert r4.status_code == 200
        assert isinstance(r4.json(), list)
        assert r4.json()[0]["rating"] == 5

    def test_create_review_invalid_rating(self, client, db):
        _, pid = _seed_seller_with_product(db)
        cust_uid = _seed_purchaser(db, email="bad@example.com", with_order=True)
        db.orders.insert_one({
            "customer_id": ObjectId(cust_uid),
            "items": [{"product_id": ObjectId(pid), "seller_id": ObjectId(), "product_name": "x", "quantity": 1, "unit_price": 10, "subtotal": 10, "seller_status": "delivered"}],
            "total_amount": 10,
            "shipping_address": {"name": "x", "phone": "1", "address": "y"},
            "status": "delivered",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        token = _make_token(cust_uid)
        r = client.post(
            f"/api/products/{pid}/reviews",
            json={"rating": 7, "title": "x", "body": "x"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 422  # pydantic validation
