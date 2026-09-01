import pytest
from datetime import datetime, timezone
from bson import ObjectId
from app.core.security import hash_password
import app.services.email_service as email_service_mod


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


def add_to_cart(client, token, product_id, quantity=1):
    return client.post("/api/cart/items", json={"product_id": product_id, "quantity": quantity}, headers=auth(token))


SHIPPING = {"name": "John Doe", "phone": "01700000000", "address": "Dhaka, Bangladesh"}


class TestOrderCheckout:
    def _setup(self, db, client):
        uid = create_user(db, "orderuser@example.com", name="Order User")
        token = login(client, "orderuser@example.com")
        seller_uid = create_user(db, "orderseller@example.com", name="Seller", role="seller")
        seller_id = create_seller(db, seller_uid, "Test Shop")
        cat_id = create_category(db)
        product_id = create_product(db, seller_id, cat_id, "Widget", 25.0, 10)
        return uid, token, seller_id, cat_id, product_id

    def test_checkout_success(self, client, db):
        uid, token, seller_id, cat_id, product_id = self._setup(db, client)
        add_to_cart(client, token, product_id, 3)

        resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 3
        assert data["items"][0]["unit_price"] == 25.0
        assert data["items"][0]["subtotal"] == 75.0
        assert data["total_amount"] == 75.0
        assert data["shipping_address"]["name"] == "John Doe"

    def test_checkout_reduces_stock(self, client, db):
        uid, token, seller_id, cat_id, product_id = self._setup(db, client)
        add_to_cart(client, token, product_id, 3)
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))

        product = db.products.find_one({"_id": ObjectId(product_id)})
        assert product["stock"] == 7

    def test_checkout_clears_cart(self, client, db):
        uid, token, seller_id, cat_id, product_id = self._setup(db, client)
        add_to_cart(client, token, product_id, 2)
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))

        resp = client.get("/api/cart", headers=auth(token))
        assert resp.json()["items"] == []

    def test_checkout_empty_cart(self, client, db):
        uid, token, _, _, _ = self._setup(db, client)
        resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

    def test_checkout_insufficient_stock(self, client, db):
        uid, token, seller_id, cat_id, product_id = self._setup(db, client)
        add_to_cart(client, token, product_id, 5)
        product = db.products.find_one({"_id": ObjectId(product_id)})
        db.products.update_one({"_id": ObjectId(product_id)}, {"$set": {"stock": 2}})
        resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        assert resp.status_code == 400
        assert "stock" in resp.json()["detail"].lower()
        db.products.update_one({"_id": ObjectId(product_id)}, {"$set": {"stock": product["stock"]}})

    def test_checkout_missing_shipping(self, client, db):
        uid, token, seller_id, cat_id, product_id = self._setup(db, client)
        add_to_cart(client, token, product_id, 1)
        resp = client.post("/api/orders", json={"shipping_address": {}}, headers=auth(token))
        assert resp.status_code == 422

    def test_checkout_requires_auth(self, client, db):
        resp = client.post("/api/orders", json={"shipping_address": SHIPPING})
        assert resp.status_code in (401, 403)

    def test_checkout_sends_confirmation_and_seller_emails(self, client, db, monkeypatch):
        uid, token, seller_id, cat_id, product_id = self._setup(db, client)
        add_to_cart(client, token, product_id, 2)

        sent = {"customer": 0, "seller": 0}

        def fake_confirmation(self_inner, to, order, customer_name):
            sent["customer"] += 1
            return True

        def fake_seller(self_inner, to, seller_name, order, items):
            # Seller email must only include this seller's items.
            assert all(str(i["seller_id"]) == seller_id for i in items)
            sent["seller"] += 1
            return True

        monkeypatch.setattr(
            email_service_mod.EmailService, "send_order_confirmation_email", fake_confirmation
        )
        monkeypatch.setattr(
            email_service_mod.EmailService, "send_seller_order_notification", fake_seller
        )

        resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        assert resp.status_code == 201
        assert sent["customer"] == 1
        assert sent["seller"] == 1

    def test_seller_cannot_checkout(self, client, db):
        uid = create_user(db, "seller_checkout@example.com", role="seller")
        token = login(client, "seller_checkout@example.com")
        resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        assert resp.status_code == 403


class TestMultiSellerOrder:
    def test_multi_seller_checkout(self, client, db):
        uid = create_user(db, "multibuyer@example.com", name="Multi Buyer")
        token = login(client, "multibuyer@example.com")

        s1_uid = create_user(db, "seller1@example.com", name="Seller One", role="seller")
        s1_id = create_seller(db, s1_uid, "Shop One")
        s2_uid = create_user(db, "seller2@example.com", name="Seller Two", role="seller")
        s2_id = create_seller(db, s2_uid, "Shop Two")

        cat_id = create_category(db, "General")
        p1 = create_product(db, s1_id, cat_id, "Alpha", 30.0, 5)
        p2 = create_product(db, s2_id, cat_id, "Beta", 50.0, 5)

        add_to_cart(client, token, p1, 2)
        add_to_cart(client, token, p2, 1)

        resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total_amount"] == 110.0

        seller_ids = {item["seller_id"] for item in data["items"]}
        assert s1_id in seller_ids
        assert s2_id in seller_ids


class TestOrderHistory:
    def test_list_orders(self, client, db):
        uid = create_user(db, "history@example.com", name="History User")
        token = login(client, "history@example.com")
        s_uid = create_user(db, "hseller@example.com", name="Hist Seller", role="seller")
        s_id = create_seller(db, s_uid, "Hist Shop")
        cat_id = create_category(db)
        p = create_product(db, s_id, cat_id, "Thing", 10.0, 20)

        add_to_cart(client, token, p, 2)
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        add_to_cart(client, token, p, 1)
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))

        resp = client.get("/api/orders", headers=auth(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_order_detail(self, client, db):
        uid = create_user(db, "detail@example.com", name="Detail User")
        token = login(client, "detail@example.com")
        s_uid = create_user(db, "dseller@example.com", name="Detail Seller", role="seller")
        s_id = create_seller(db, s_uid, "Detail Shop")
        cat_id = create_category(db)
        p = create_product(db, s_id, cat_id, "DetailWidget", 40.0, 10)

        add_to_cart(client, token, p, 1)
        order_resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token))
        order_id = order_resp.json()["id"]

        resp = client.get(f"/api/orders/{order_id}", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["id"] == order_id
        assert resp.json()["total_amount"] == 40.0

    def test_cannot_view_other_order(self, client, db):
        uid1 = create_user(db, "user1@example.com", name="User 1")
        token1 = login(client, "user1@example.com")
        uid2 = create_user(db, "user2@example.com", name="User 2")
        token2 = login(client, "user2@example.com")

        s_uid = create_user(db, "oseller@example.com", name="OSeller", role="seller")
        s_id = create_seller(db, s_uid, "OShop")
        cat_id = create_category(db)
        p = create_product(db, s_id, cat_id, "Secure", 15.0, 10)

        add_to_cart(client, token1, p, 1)
        order_resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(token1))
        order_id = order_resp.json()["id"]

        resp = client.get(f"/api/orders/{order_id}", headers=auth(token2))
        assert resp.status_code == 403

    def test_order_not_found(self, client, db):
        uid = create_user(db, "nf@example.com", name="NF User")
        token = login(client, "nf@example.com")
        fake_id = str(ObjectId())
        resp = client.get(f"/api/orders/{fake_id}", headers=auth(token))
        assert resp.status_code == 404
