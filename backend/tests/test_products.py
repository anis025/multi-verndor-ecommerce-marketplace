import pytest
from datetime import datetime, timezone
from bson import ObjectId
from app.core.security import hash_password


def create_user(db, email, name="User", role="customer", is_active=True):
    result = db.users.insert_one({
        "name": name, "email": email,
        "password_hash": hash_password("password123"),
        "role": role, "is_active": is_active, "email_verified": True,
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


def create_category(db, name="Electronics", is_active=True):
    result = db.categories.insert_one({
        "name": name, "description": f"{name} products",
        "is_active": is_active,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def login(client, email):
    resp = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ==================== CATEGORY TESTS ====================

class TestCategoryAdmin:
    def _admin(self, db, client):
        uid = create_user(db, "admin_cat@example.com", role="admin")
        return login(client, "admin_cat@example.com")

    def test_create_category(self, client, db):
        token = self._admin(db, client)
        resp = client.post("/api/admin/categories", json={
            "name": "Electronics", "description": "Electronic products"
        }, headers=auth(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Electronics"
        assert data["is_active"] is True

    def test_duplicate_category(self, client, db):
        token = self._admin(db, client)
        client.post("/api/admin/categories", json={"name": "Dup Cat"}, headers=auth(token))
        resp = client.post("/api/admin/categories", json={"name": "Dup Cat"}, headers=auth(token))
        assert resp.status_code == 409

    def test_update_category(self, client, db):
        token = self._admin(db, client)
        cat_resp = client.post("/api/admin/categories", json={"name": "Update Me"}, headers=auth(token))
        cat_id = cat_resp.json()["id"]
        resp = client.patch(f"/api/admin/categories/{cat_id}",
                           json={"name": "Updated Cat"}, headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Cat"

    def test_delete_category(self, client, db):
        token = self._admin(db, client)
        cat_resp = client.post("/api/admin/categories", json={"name": "Delete Me"}, headers=auth(token))
        cat_id = cat_resp.json()["id"]
        resp = client.delete(f"/api/admin/categories/{cat_id}", headers=auth(token))
        assert resp.status_code == 200

    def test_customer_cannot_create_category(self, client, db):
        uid = create_user(db, "cust_cat@example.com", role="customer")
        token = login(client, "cust_cat@example.com")
        resp = client.post("/api/admin/categories", json={"name": "Nope"}, headers=auth(token))
        assert resp.status_code == 403

    def test_seller_cannot_create_category(self, client, db):
        uid = create_user(db, "sell_cat@example.com", role="seller")
        token = login(client, "sell_cat@example.com")
        resp = client.post("/api/admin/categories", json={"name": "Nope"}, headers=auth(token))
        assert resp.status_code == 403


class TestCategoryPublic:
    def test_list_categories(self, client, db):
        uid = create_user(db, "admin_list@example.com", role="admin")
        token = login(client, "admin_list@example.com")
        client.post("/api/admin/categories", json={"name": "Cat1"}, headers=auth(token))
        client.post("/api/admin/categories", json={"name": "Cat2"}, headers=auth(token))

        resp = client.get("/api/categories/active")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 2

    def test_get_category(self, client, db):
        uid = create_user(db, "admin_getcat@example.com", role="admin")
        token = login(client, "admin_getcat@example.com")
        cat_resp = client.post("/api/admin/categories", json={"name": "GetCat"}, headers=auth(token))
        cat_id = cat_resp.json()["id"]

        resp = client.get(f"/api/categories/{cat_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "GetCat"

    def test_invalid_category_id(self, client):
        resp = client.get("/api/categories/invalidid")
        assert resp.status_code == 400

    def test_category_not_found(self, client):
        fake_id = str(ObjectId())
        resp = client.get(f"/api/categories/{fake_id}")
        assert resp.status_code == 404


# ==================== PRODUCT TESTS ====================

class TestProductCRUD:
    def _seller(self, db, client):
        uid = create_user(db, "seller_prod@example.com", role="seller")
        sid = create_seller(db, uid, "Prod Corp", is_approved=True)
        token = login(client, "seller_prod@example.com")
        return uid, sid, token

    def _category(self, db, client):
        uid = create_user(db, "admin_pc@example.com", role="admin")
        token = login(client, "admin_pc@example.com")
        cat_resp = client.post("/api/admin/categories", json={"name": "ProdCat"}, headers=auth(token))
        return cat_resp.json()["id"]

    def test_create_product(self, client, db):
        uid, sid, token = self._seller(db, client)
        cat_id = self._category(db, client)
        resp = client.post("/api/sellers/me/products", json={
            "name": "Laptop", "description": "Gaming laptop",
            "price": 999.99, "stock": 10, "category_id": cat_id,
        }, headers=auth(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Laptop"
        assert data["price"] == 999.99
        assert data["stock"] == 10
        assert data["company_name"] == "Prod Corp"

    def test_list_seller_products(self, client, db):
        uid, sid, token = self._seller(db, client)
        cat_id = self._category(db, client)
        client.post("/api/sellers/me/products", json={
            "name": "P1", "price": 10, "stock": 5, "category_id": cat_id,
        }, headers=auth(token))
        resp = client.get("/api/sellers/me/products", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_update_product(self, client, db):
        uid, sid, token = self._seller(db, client)
        cat_id = self._category(db, client)
        prod_resp = client.post("/api/sellers/me/products", json={
            "name": "UpdProd", "price": 50, "stock": 5, "category_id": cat_id,
        }, headers=auth(token))
        prod_id = prod_resp.json()["id"]
        resp = client.patch(f"/api/sellers/me/products/{prod_id}",
                           json={"name": "UpdatedProd", "price": 75}, headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["name"] == "UpdatedProd"
        assert resp.json()["price"] == 75

    def test_delete_product(self, client, db):
        uid, sid, token = self._seller(db, client)
        cat_id = self._category(db, client)
        prod_resp = client.post("/api/sellers/me/products", json={
            "name": "DelProd", "price": 30, "stock": 2, "category_id": cat_id,
        }, headers=auth(token))
        prod_id = prod_resp.json()["id"]
        resp = client.delete(f"/api/sellers/me/products/{prod_id}", headers=auth(token))
        assert resp.status_code == 200

    def test_negative_price_rejected(self, client, db):
        uid, sid, token = self._seller(db, client)
        cat_id = self._category(db, client)
        resp = client.post("/api/sellers/me/products", json={
            "name": "Bad Price", "price": -10, "stock": 5, "category_id": cat_id,
        }, headers=auth(token))
        assert resp.status_code == 422

    def test_negative_stock_rejected(self, client, db):
        uid, sid, token = self._seller(db, client)
        cat_id = self._category(db, client)
        resp = client.post("/api/sellers/me/products", json={
            "name": "Bad Stock", "price": 10, "stock": -5, "category_id": cat_id,
        }, headers=auth(token))
        assert resp.status_code == 422


class TestProductOwnership:
    def test_seller_cannot_modify_other_product(self, client, db):
        uid1 = create_user(db, "s1_own@example.com", role="seller")
        sid1 = create_seller(db, uid1, "Corp1", is_approved=True)
        token1 = login(client, "s1_own@example.com")

        uid2 = create_user(db, "s2_own@example.com", role="seller")
        sid2 = create_seller(db, uid2, "Corp2", is_approved=True)
        token2 = login(client, "s2_own@example.com")

        uid_admin = create_user(db, "admin_own@example.com", role="admin")
        admin_token = login(client, "admin_own@example.com")
        cat_resp = client.post("/api/admin/categories", json={"name": "OwnCat"}, headers=auth(admin_token))
        cat_id = cat_resp.json()["id"]

        prod_resp = client.post("/api/sellers/me/products", json={
            "name": "S1 Product", "price": 10, "stock": 5, "category_id": cat_id,
        }, headers=auth(token1))
        prod_id = prod_resp.json()["id"]

        resp = client.patch(f"/api/sellers/me/products/{prod_id}",
                           json={"name": "Hacked"}, headers=auth(token2))
        assert resp.status_code == 403

    def test_seller_cannot_delete_other_product(self, client, db):
        uid1 = create_user(db, "s1_del@example.com", role="seller")
        sid1 = create_seller(db, uid1, "DelCorp1", is_approved=True)
        token1 = login(client, "s1_del@example.com")

        uid2 = create_user(db, "s2_del@example.com", role="seller")
        sid2 = create_seller(db, uid2, "DelCorp2", is_approved=True)
        token2 = login(client, "s2_del@example.com")

        uid_admin = create_user(db, "admin_del@example.com", role="admin")
        admin_token = login(client, "admin_del@example.com")
        cat_resp = client.post("/api/admin/categories", json={"name": "DelCat"}, headers=auth(admin_token))
        cat_id = cat_resp.json()["id"]

        prod_resp = client.post("/api/sellers/me/products", json={
            "name": "DelS1", "price": 10, "stock": 5, "category_id": cat_id,
        }, headers=auth(token1))
        prod_id = prod_resp.json()["id"]

        resp = client.delete(f"/api/sellers/me/products/{prod_id}", headers=auth(token2))
        assert resp.status_code == 403


class TestProductPublic:
    def _setup(self, db, client):
        uid = create_user(db, "pub_admin@example.com", role="admin")
        admin_token = login(client, "pub_admin@example.com")
        cat_resp = client.post("/api/admin/categories", json={"name": "PubCat"}, headers=auth(admin_token))
        cat_id = cat_resp.json()["id"]

        uid_s = create_user(db, "pub_seller@example.com", role="seller")
        create_seller(db, uid_s, "PubCorp", is_approved=True)
        seller_token = login(client, "pub_seller@example.com")

        client.post("/api/sellers/me/products", json={
            "name": "PubLaptop", "description": "Gaming laptop",
            "price": 999, "stock": 10, "category_id": cat_id,
        }, headers=auth(seller_token))
        return cat_id

    def test_list_products(self, client, db):
        self._setup(db, client)
        resp = client.get("/api/products")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert "total_pages" in data

    def test_product_details(self, client, db):
        self._setup(db, client)
        resp = client.get("/api/products")
        prod_id = resp.json()["items"][0]["id"]
        resp = client.get(f"/api/products/{prod_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "PubLaptop"

    def test_search_products(self, client, db):
        self._setup(db, client)
        resp = client.get("/api/products?search=Laptop")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_price_filter(self, client, db):
        self._setup(db, client)
        resp = client.get("/api/products?min_price=500&max_price=1500")
        assert resp.status_code == 200

    def test_pagination(self, client, db):
        self._setup(db, client)
        resp = client.get("/api/products?page=1&limit=5")
        data = resp.json()
        assert data["page"] == 1
        assert data["limit"] == 5

    def test_invalid_product_id(self, client):
        resp = client.get("/api/products/invalidid")
        assert resp.status_code == 400

    def test_product_not_found(self, client):
        fake_id = str(ObjectId())
        resp = client.get(f"/api/products/{fake_id}")
        assert resp.status_code == 404


class TestSellerApprovalIntegration:
    def test_pending_seller_cannot_create_product(self, client, db):
        uid = create_user(db, "pending_s@example.com", role="seller")
        create_seller(db, uid, "PendingCorp", is_approved=False)
        token = login(client, "pending_s@example.com")
        uid_admin = create_user(db, "admin_pend@example.com", role="admin")
        admin_token = login(client, "admin_pend@example.com")
        cat_resp = client.post("/api/admin/categories", json={"name": "PendCat"}, headers=auth(admin_token))
        cat_id = cat_resp.json()["id"]
        resp = client.post("/api/sellers/me/products", json={
            "name": "Should Fail", "price": 10, "stock": 5, "category_id": cat_id,
        }, headers=auth(token))
        assert resp.status_code == 403


class TestAdminProductManagement:
    def _admin(self, db, client):
        uid = create_user(db, "admin_prodmgmt@example.com", role="admin")
        return login(client, "admin_prodmgmt@example.com")

    def _seller_product(self, db, client):
        uid = create_user(db, "seller_am@example.com", role="seller")
        sid = create_seller(db, uid, "AMCorp", is_approved=True)
        token = login(client, "seller_am@example.com")
        uid_admin = create_user(db, "admin_am@example.com", role="admin")
        admin_token = login(client, "admin_am@example.com")
        cat_resp = client.post("/api/admin/categories", json={"name": "AMCat"}, headers=auth(admin_token))
        cat_id = cat_resp.json()["id"]
        prod_resp = client.post("/api/sellers/me/products", json={
            "name": "AM Product", "price": 100, "stock": 10, "category_id": cat_id,
        }, headers=auth(token))
        return prod_resp.json()["id"]

    def test_admin_list_products(self, client, db):
        token = self._admin(db, client)
        self._seller_product(db, client)
        resp = client.get("/api/admin/products", headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_admin_get_product(self, client, db):
        token = self._admin(db, client)
        prod_id = self._seller_product(db, client)
        resp = client.get(f"/api/admin/products/{prod_id}", headers=auth(token))
        assert resp.status_code == 200

    def test_admin_update_product(self, client, db):
        token = self._admin(db, client)
        prod_id = self._seller_product(db, client)
        resp = client.patch(f"/api/admin/products/{prod_id}",
                           json={"name": "Admin Updated"}, headers=auth(token))
        assert resp.status_code == 200
        assert resp.json()["name"] == "Admin Updated"

    def test_admin_delete_product(self, client, db):
        token = self._admin(db, client)
        prod_id = self._seller_product(db, client)
        resp = client.delete(f"/api/admin/products/{prod_id}", headers=auth(token))
        assert resp.status_code == 200

    def test_customer_cannot_access_admin_products(self, client, db):
        uid = create_user(db, "cust_aprod@example.com", role="customer")
        token = login(client, "cust_aprod@example.com")
        resp = client.get("/api/admin/products", headers=auth(token))
        assert resp.status_code == 403

    def test_seller_cannot_access_admin_products(self, client, db):
        uid = create_user(db, "sell_aprod@example.com", role="seller")
        token = login(client, "sell_aprod@example.com")
        resp = client.get("/api/admin/products", headers=auth(token))
        assert resp.status_code == 403


class TestSecurityPhase5:
    def test_customer_cannot_create_product(self, client, db):
        uid = create_user(db, "cust_noprod@example.com", role="customer")
        token = login(client, "cust_noprod@example.com")
        resp = client.post("/api/sellers/me/products", json={
            "name": "Nope", "price": 10, "stock": 5, "category_id": str(ObjectId()),
        }, headers=auth(token))
        assert resp.status_code == 403

    def test_unauthenticated_cannot_create_product(self, client):
        resp = client.post("/api/sellers/me/products", json={
            "name": "Nope", "price": 10, "stock": 5, "category_id": str(ObjectId()),
        })
        assert resp.status_code in (401, 403)

    def test_health_still_works(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
