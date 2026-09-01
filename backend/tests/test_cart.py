import pytest
from datetime import datetime, timezone
from bson import ObjectId
from app.core.security import hash_password


def create_user(db, email, name="User", role="customer"):
    result = db.users.insert_one({
        "name": name, "email": email,
        "password_hash": hash_password("password123"),
        "role": role, "is_active": True, "email_verified": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def create_seller(db, user_id, company_name="Corp", is_approved=True):
    result = db.sellers.insert_one({
        "user_id": ObjectId(user_id), "company_name": company_name,
        "description": "Test", "phone": "01700000000", "address": "Dhaka",
        "is_approved": is_approved,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def create_category(db, name="Electronics"):
    result = db.categories.insert_one({
        "name": name, "description": f"{name} products",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def create_product(db, seller_id, category_id, name="Test Product", price=100, stock=10):
    result = db.products.insert_one({
        "seller_id": ObjectId(seller_id), "category_id": ObjectId(category_id),
        "name": name, "description": "Test", "price": price,
        "stock": stock, "image_url": "", "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def login(client, email):
    resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestCart:
    def _setup(self, db, client):
        uid = create_user(db, "cartuser@example.com", name="Cart User")
        token = login(client, "cartuser@example.com")
        seller_id = create_seller(db, uid)
        cat_id = create_category(db)
        product_id = create_product(db, seller_id, cat_id, "Widget", 25.0, 10)
        return uid, token, seller_id, cat_id, product_id

    def test_get_empty_cart(self, client, db):
        uid, token, _, _, _ = self._setup(db, client)
        resp = client.get("/api/cart", headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["item_count"] == 0

    def test_add_to_cart(self, client, db):
        uid, token, _, _, product_id = self._setup(db, client)
        resp = client.post("/api/cart/items", json={
            "product_id": product_id, "quantity": 2
        }, headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["subtotal"] == 50.0
        assert data["total"] == 50.0
        assert data["item_count"] == 2

    def test_add_increments_quantity(self, client, db):
        uid, token, _, _, product_id = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1}, headers=auth(token))
        resp = client.post("/api/cart/items", json={"product_id": product_id, "quantity": 2}, headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 3

    def test_add_insufficient_stock(self, client, db):
        uid, token, _, _, product_id = self._setup(db, client)
        resp = client.post("/api/cart/items", json={"product_id": product_id, "quantity": 99}, headers=auth(token))
        assert resp.status_code == 400
        assert "stock" in resp.json()["detail"].lower()

    def test_add_nonexistent_product(self, client, db):
        uid, token, _, _, _ = self._setup(db, client)
        fake_id = str(ObjectId())
        resp = client.post("/api/cart/items", json={"product_id": fake_id, "quantity": 1}, headers=auth(token))
        assert resp.status_code == 400
        assert "not found" in resp.json()["detail"].lower()

    def test_update_cart_item(self, client, db):
        uid, token, _, _, product_id = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1}, headers=auth(token))
        resp = client.put(f"/api/cart/items/{product_id}", json={"quantity": 5}, headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["items"][0]["quantity"] == 5
        assert resp.json()["items"][0]["subtotal"] == 125.0

    def test_update_insufficient_stock(self, client, db):
        uid, token, _, _, product_id = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1}, headers=auth(token))
        resp = client.put(f"/api/cart/items/{product_id}", json={"quantity": 99}, headers=auth(token))
        assert resp.status_code == 400

    def test_remove_from_cart(self, client, db):
        uid, token, _, _, product_id = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1}, headers=auth(token))
        resp = client.delete(f"/api/cart/items/{product_id}", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_remove_nonexistent_item(self, client, db):
        uid, token, _, _, _ = self._setup(db, client)
        fake_id = str(ObjectId())
        resp = client.delete(f"/api/cart/items/{fake_id}", headers=auth(token))
        assert resp.status_code == 404

    def test_clear_cart(self, client, db):
        uid, token, _, _, product_id = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": product_id, "quantity": 3}, headers=auth(token))
        resp = client.delete("/api/cart", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["items"] == []
        assert resp.json()["total"] == 0

    def test_multiple_products_in_cart(self, client, db):
        uid, token, seller_id, cat_id = self._setup(db, client)[:4]
        product2 = create_product(db, seller_id, cat_id, "Gadget", 50.0, 5)
        client.post("/api/cart/items", json={"product_id": product2, "quantity": 1}, headers=auth(token))
        p1 = create_product(db, seller_id, cat_id, "Thing", 30.0, 7)
        client.post("/api/cart/items", json={"product_id": p1, "quantity": 2}, headers=auth(token))

        resp = client.get("/api/cart", headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["item_count"] == 3

    def test_cart_requires_auth(self, client, db):
        resp = client.get("/api/cart")
        assert resp.status_code in (401, 403)

    def test_seller_cannot_use_cart(self, client, db):
        uid = create_user(db, "seller_cart@example.com", role="seller")
        token = login(client, "seller_cart@example.com")
        resp = client.get("/api/cart", headers=auth(token))
        assert resp.status_code == 403
