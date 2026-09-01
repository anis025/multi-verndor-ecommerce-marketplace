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


class TestAdminOrders:
    def _setup(self, db, client):
        admin_uid = create_user(db, "admin_orders@example.com", role="admin")
        admin_token = login(client, "admin_orders@example.com")

        s_uid = create_user(db, "aorder_seller@example.com", role="seller")
        s_id = create_seller(db, s_uid, "AO Shop")
        b_uid = create_user(db, "aorder_buyer@example.com")
        b_token = login(client, "aorder_buyer@example.com")

        cat_id = create_category(db)
        p1 = create_product(db, s_id, cat_id, "AWidget", 25.0, 10)
        return admin_token, b_token, s_id, cat_id, p1

    def test_admin_list_orders(self, client, db):
        admin_token, b_token, s_id, cat_id, p1 = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": p1, "quantity": 2}, headers=auth(b_token))
        client.post("/api/orders", json={"shipping_address": {"name": "J", "phone": "017", "address": "Dhaka"}}, headers=auth(b_token))

        resp = client.get("/api/admin/orders", headers=auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_admin_get_order(self, client, db):
        admin_token, b_token, s_id, cat_id, p1 = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        order_resp = client.post("/api/orders", json={"shipping_address": {"name": "J", "phone": "017", "address": "Dhaka"}}, headers=auth(b_token))
        order_id = order_resp.json()["id"]

        resp = client.get(f"/api/admin/orders/{order_id}", headers=auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["id"] == order_id

    def test_admin_update_order_status(self, client, db):
        admin_token, b_token, s_id, cat_id, p1 = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        order_resp = client.post("/api/orders", json={"shipping_address": {"name": "J", "phone": "017", "address": "Dhaka"}}, headers=auth(b_token))
        order_id = order_resp.json()["id"]

        resp = client.put(f"/api/admin/orders/{order_id}/status", json={"status": "confirmed"}, headers=auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

    def test_admin_invalid_status(self, client, db):
        admin_token, b_token, s_id, cat_id, p1 = self._setup(db, client)
        client.post("/api/cart/items", json={"product_id": p1, "quantity": 1}, headers=auth(b_token))
        order_resp = client.post("/api/orders", json={"shipping_address": {"name": "J", "phone": "017", "address": "Dhaka"}}, headers=auth(b_token))
        order_id = order_resp.json()["id"]

        resp = client.put(f"/api/admin/orders/{order_id}/status", json={"status": "bogus"}, headers=auth(admin_token))
        assert resp.status_code == 400

    def test_customer_cannot_access_admin_orders(self, client, db):
        b_uid = create_user(db, "aorder_cust@example.com")
        b_token = login(client, "aorder_cust@example.com")
        resp = client.get("/api/admin/orders", headers=auth(b_token))
        assert resp.status_code == 403


class TestAdminDashboard:
    def test_dashboard_stats(self, client, db):
        admin_uid = create_user(db, "admin_dash@example.com", role="admin")
        admin_token = login(client, "admin_dash@example.com")

        s_uid = create_user(db, "dash_seller@example.com", role="seller")
        create_seller(db, s_uid, "Dash Shop")
        create_user(db, "dash_buyer@example.com")

        cat_id = create_category(db)
        create_product(db, s_uid, cat_id, "DashWidget", 50.0, 10)

        resp = client.get("/api/admin/dashboard", headers=auth(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "total_sellers" in data
        assert "total_products" in data
        assert "total_orders" in data
        assert "total_revenue" in data
        assert data["total_users"] >= 1
        assert data["total_sellers"] >= 1
        assert data["total_products"] >= 1

    def test_customer_cannot_access_dashboard(self, client, db):
        b_uid = create_user(db, "dash_cust@example.com")
        b_token = login(client, "dash_cust@example.com")
        resp = client.get("/api/admin/dashboard", headers=auth(b_token))
        assert resp.status_code == 403

class TestAdminUserManagement:
    def _setup(self, db, client):
        admin_id = create_user(db, "admin_um@example.com", name="Admin", role="admin")
        admin_token = login(client, "admin_um@example.com")
        return admin_token

    def test_reset_password_returns_generated_password(self, client, db):
        admin_token = self._setup(db, client)
        target_id = create_user(db, "reset_target@example.com", name="Target")
        resp = client.post(
            f"/api/admin/users/{target_id}/reset-password",
            json={},
            headers=auth(admin_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "new_password" in data
        new_pwd = data["new_password"]
        assert len(new_pwd) >= 8
        # The user can now log in with the generated password.
        login_resp = client.post("/api/auth/login", json={
            "email": "reset_target@example.com",
            "password": new_pwd,
        })
        assert login_resp.status_code == 200

    def test_change_role(self, client, db):
        admin_token = self._setup(db, client)
        target_id = create_user(db, "role_target@example.com", role="customer")
        resp = client.post(
            f"/api/admin/users/{target_id}/role",
            json={"role": "seller"},
            headers=auth(admin_token),
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "seller"

    def test_change_role_invalid(self, client, db):
        admin_token = self._setup(db, client)
        target_id = create_user(db, "role_bad@example.com")
        resp = client.post(
            f"/api/admin/users/{target_id}/role",
            json={"role": "god"},
            headers=auth(admin_token),
        )
        # Pydantic enum validation rejects the unknown role.
        assert resp.status_code == 422

    def test_verify_email(self, client, db):
        admin_token = self._setup(db, client)
        target_id = create_user(db, "verify_target@example.com")
        # Set email_verified=False explicitly.
        db.users.update_one({"_id": __import__("bson").ObjectId(target_id)},
                            {"$set": {"email_verified": False}})
        resp = client.post(
            f"/api/admin/users/{target_id}/verify-email",
            headers=auth(admin_token),
        )
        assert resp.status_code == 200
        assert resp.json()["email_verified"] is True

    def test_user_detail_includes_order_summary(self, client, db):
        admin_token = self._setup(db, client)
        # Create a customer with an order.
        cust_id = create_user(db, "detail_cust@example.com", name="Detail Cust", role="customer")
        seller_uid = create_user(db, "detail_seller@example.com", role="seller")
        seller_id = create_seller(db, seller_uid, "Detail Shop")
        cat_id = create_category(db)
        product_id = create_product(db, seller_id, cat_id, "Widget", 10.0, 5)
        cust_token = login(client, "detail_cust@example.com")
        client.post("/api/cart/items", json={"product_id": product_id, "quantity": 1},
                    headers=auth(cust_token))
        client.post("/api/orders", json={"shipping_address": {"name": "x", "phone": "1", "address": "y"}},
                    headers=auth(cust_token))

        resp = client.get(f"/api/admin/users/{cust_id}", headers=auth(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["order_count"] == 1
        assert len(data["recent_orders"]) == 1
        assert data["recent_orders"][0]["item_count"] == 1

    def test_user_detail_seller_includes_product_count(self, client, db):
        admin_token = self._setup(db, client)
        seller_uid = create_user(db, "detail_seller2@example.com", role="seller")
        seller_id = create_seller(db, seller_uid, "Shop 2")
        cat_id = create_category(db)
        create_product(db, seller_id, cat_id, "P1", 5, 1)
        create_product(db, seller_id, cat_id, "P2", 6, 1)
        resp = client.get(f"/api/admin/users/{seller_uid}", headers=auth(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["product_count"] == 2
        assert data["seller_status"] in ("pending", "approved", "rejected", "suspended")

    def test_non_admin_cannot_use_user_mgmt_endpoints(self, client, db):
        target_id = create_user(db, "noadm_target@example.com")
        b_uid = create_user(db, "noadm_user@example.com", role="customer")
        b_token = login(client, "noadm_user@example.com")
        # Each must be 403.
        for path, method, body in [
            (f"/api/admin/users/{target_id}/reset-password", "post", {}),
            (f"/api/admin/users/{target_id}/role", "post", {"role": "seller"}),
            (f"/api/admin/users/{target_id}/verify-email", "post", None),
        ]:
            kwargs = {"headers": auth(b_token)}
            if body is not None:
                kwargs["json"] = body
            resp = getattr(client, method)(path, **kwargs)
            assert resp.status_code == 403, (path, resp.status_code)
