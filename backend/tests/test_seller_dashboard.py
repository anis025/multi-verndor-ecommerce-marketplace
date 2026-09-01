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


def create_order(db, customer_id, items, total=100, shipping=None):
    now = datetime.now(timezone.utc)
    if shipping is None:
        shipping = {"name": "John", "phone": "017", "address": "Dhaka"}
    result = db.orders.insert_one({
        "customer_id": ObjectId(customer_id),
        "items": items,
        "total_amount": total,
        "shipping_address": shipping,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    })
    return str(result.inserted_id)


def login(client, email):
    resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


SHIPPING = {"name": "John Doe", "phone": "01700000000", "address": "Dhaka"}


class TestSellerOrders:
    def _setup(self, db, client):
        seller_uid = create_user(db, "sorder_seller@example.com", name="Seller", role="seller")
        seller_token = login(client, "sorder_seller@example.com")
        seller_id = create_seller(db, seller_uid, "Seller Shop")

        buyer_uid = create_user(db, "sorder_buyer@example.com", name="Buyer")
        buyer_token = login(client, "sorder_buyer@example.com")

        cat_id = create_category(db)
        p1 = create_product(db, seller_id, cat_id, "Widget", 25.0, 10)

        return seller_uid, seller_token, seller_id, buyer_uid, buyer_token, cat_id, p1

    def test_seller_list_orders(self, client, db):
        s_uid, s_token, s_id, b_uid, b_token, cat_id, p1 = self._setup(db, client)

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 2}, headers=auth(b_token))
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))

        resp = client.get("/api/seller/orders", headers=auth(s_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_seller_get_order_detail(self, client, db):
        s_uid, s_token, s_id, b_uid, b_token, cat_id, p1 = self._setup(db, client)

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        order_resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))
        order_id = order_resp.json()["id"]

        resp = client.get(f"/api/seller/orders/{order_id}", headers=auth(s_token))
        assert resp.status_code == 200
        assert resp.json()["id"] == order_id

    def test_seller_cannot_view_other_order(self, client, db):
        s_uid, s_token, s_id, b_uid, b_token, cat_id, p1 = self._setup(db, client)

        other_s_uid = create_user(db, "other_seller@example.com", role="seller")
        other_s_token = login(client, "other_seller@example.com")
        create_seller(db, other_s_uid, "Other Shop")

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        order_resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))
        order_id = order_resp.json()["id"]

        resp = client.get(f"/api/seller/orders/{order_id}", headers=auth(other_s_token))
        assert resp.status_code == 403

    def test_seller_update_item_status(self, client, db):
        s_uid, s_token, s_id, b_uid, b_token, cat_id, p1 = self._setup(db, client)

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        order_resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))
        order_id = order_resp.json()["id"]

        resp = client.put(
            f"/api/seller/orders/{order_id}/items/{p1}/status",
            json={"status": "confirmed"},
            headers=auth(s_token),
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert items[0]["seller_status"] == "confirmed"

    def test_seller_invalid_status(self, client, db):
        s_uid, s_token, s_id, b_uid, b_token, cat_id, p1 = self._setup(db, client)

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        order_resp = client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))
        order_id = order_resp.json()["id"]

        resp = client.put(
            f"/api/seller/orders/{order_id}/items/{p1}/status",
            json={"status": "bogus"},
            headers=auth(s_token),
        )
        assert resp.status_code == 400


class TestNotifications:
    def test_get_notifications_empty(self, client, db):
        uid = create_user(db, "notif_empty@example.com")
        token = login(client, "notif_empty@example.com")
        resp = client.get("/api/notifications", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["unread_count"] == 0

    def test_notifications_created_on_order(self, client, db):
        s_uid = create_user(db, "notif_seller@example.com", role="seller")
        s_id = create_seller(db, s_uid, "Notif Shop")
        b_uid = create_user(db, "notif_buyer@example.com")
        b_token = login(client, "notif_buyer@example.com")
        s_token = login(client, "notif_seller@example.com")

        cat_id = create_category(db)
        p1 = create_product(db, s_id, cat_id, "Thing", 20.0, 5)

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))

        resp = client.get("/api/notifications", headers=auth(s_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["unread_count"] == 1
        assert data["items"][0]["type"] == "new_order"

    def test_mark_notification_read(self, client, db):
        s_uid = create_user(db, "notif_read@example.com", role="seller")
        s_id = create_seller(db, s_uid, "Read Shop")
        b_uid = create_user(db, "notif_read_buyer@example.com")
        b_token = login(client, "notif_read_buyer@example.com")
        s_token = login(client, "notif_read@example.com")

        cat_id = create_category(db)
        p1 = create_product(db, s_id, cat_id, "ReadItem", 30.0, 5)

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))

        notifs = client.get("/api/notifications", headers=auth(s_token)).json()
        notif_id = notifs["items"][0]["id"]

        resp = client.put(f"/api/notifications/{notif_id}/read", headers=auth(s_token))
        assert resp.status_code == 200

        notifs2 = client.get("/api/notifications", headers=auth(s_token)).json()
        assert notifs2["unread_count"] == 0

    def test_mark_all_read(self, client, db):
        s_uid = create_user(db, "notif_readall@example.com", role="seller")
        s_id = create_seller(db, s_uid, "ReadAll Shop")
        b_uid = create_user(db, "notif_readall_buyer@example.com")
        b_token = login(client, "notif_readall_buyer@example.com")
        s_token = login(client, "notif_readall@example.com")

        cat_id = create_category(db)
        p1 = create_product(db, s_id, cat_id, "ReadAllItem", 15.0, 10)

        client.post("/api/cart/items", json={"product_id": p1, "quantity": 2}, headers=auth(b_token))
        client.post("/api/orders", json={"shipping_address": SHIPPING}, headers=auth(b_token))

        resp = client.put("/api/notifications/read-all", headers=auth(s_token))
        assert resp.status_code == 200

        notifs = client.get("/api/notifications", headers=auth(s_token)).json()
        assert notifs["unread_count"] == 0

    def test_notifications_requires_auth(self, client, db):
        resp = client.get("/api/notifications")
        assert resp.status_code in (401, 403)
