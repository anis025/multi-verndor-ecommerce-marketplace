import pytest
from datetime import datetime, timezone
from app.core.security import hash_password


def create_test_user(db, email="test@example.com", name="Test User", role="customer", is_active=True):
    result = db.users.insert_one({
        "name": name,
        "email": email,
        "password_hash": hash_password("password123"),
        "role": role,
        "is_active": is_active,
        "email_verified": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def create_test_seller(db, user_id, company_name="Test Corp", is_approved=False):
    from bson import ObjectId
    result = db.sellers.insert_one({
        "user_id": ObjectId(user_id),
        "company_name": company_name,
        "description": "Test seller",
        "phone": "01700000000",
        "address": "Dhaka, Bangladesh",
        "is_approved": is_approved,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    return str(result.inserted_id)


def login_user(client, email, password="password123"):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ==================== USER PROFILE TESTS ====================

class TestUserProfile:
    def test_get_profile(self, client, db):
        user_id = create_test_user(db, email="profile@example.com")
        token = login_user(client, "profile@example.com")
        resp = client.get("/api/users/me", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "profile@example.com"
        assert data["name"] == "Test User"
        assert data["role"] == "customer"

    def test_update_profile(self, client, db):
        user_id = create_test_user(db, email="update@example.com")
        token = login_user(client, "update@example.com")
        resp = client.patch("/api/users/me", json={"name": "Updated Name"}, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Name"

    def test_unauthenticated_profile(self, client):
        resp = client.get("/api/users/me")
        assert resp.status_code in (401, 403)

    def test_password_hash_not_returned(self, client, db):
        user_id = create_test_user(db, email="nohash@example.com")
        token = login_user(client, "nohash@example.com")
        resp = client.get("/api/users/me", headers=auth_header(token))
        data = resp.json()
        assert "password_hash" not in data
        assert "password" not in data


# ==================== PASSWORD CHANGE TESTS ====================

class TestPasswordChange:
    def test_change_password_success(self, client, db):
        user_id = create_test_user(db, email="changepass@example.com")
        token = login_user(client, "changepass@example.com")
        resp = client.patch("/api/users/me/password", json={
            "current_password": "password123",
            "new_password": "newpassword456",
        }, headers=auth_header(token))
        assert resp.status_code == 200

    def test_change_password_wrong_current(self, client, db):
        user_id = create_test_user(db, email="wrongcurrent@example.com")
        token = login_user(client, "wrongcurrent@example.com")
        resp = client.patch("/api/users/me/password", json={
            "current_password": "wrongpassword",
            "new_password": "newpassword456",
        }, headers=auth_header(token))
        assert resp.status_code == 400

    def test_change_password_new_login_works(self, client, db):
        user_id = create_test_user(db, email="newlogin@example.com")
        token = login_user(client, "newlogin@example.com")
        client.patch("/api/users/me/password", json={
            "current_password": "password123",
            "new_password": "newpass789",
        }, headers=auth_header(token))
        resp = client.post("/api/auth/login", json={"email": "newlogin@example.com", "password": "newpass789"})
        assert resp.status_code == 200


# ==================== ADMIN USER TESTS ====================

class TestAdminUsers:
    def _setup_admin(self, db, client):
        user_id = create_test_user(db, email="admin@example.com", name="Admin", role="admin")
        token = login_user(client, "admin@example.com")
        return user_id, token

    def test_admin_list_users(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        create_test_user(db, email="user1@example.com")
        create_test_user(db, email="user2@example.com")
        resp = client.get("/api/admin/users", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    def test_admin_pagination(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        for i in range(5):
            create_test_user(db, email=f"page{i}@example.com")
        resp = client.get("/api/admin/users?page=1&limit=2", headers=auth_header(token))
        data = resp.json()
        assert data["page"] == 1
        assert data["limit"] == 2
        assert len(data["items"]) == 2

    def test_admin_get_user(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        user_id = create_test_user(db, email="getuser@example.com")
        resp = client.get(f"/api/admin/users/{user_id}", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "getuser@example.com"

    def test_admin_update_user_status(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        user_id = create_test_user(db, email="statususer@example.com")
        resp = client.patch(f"/api/admin/users/{user_id}/status",
                           json={"is_active": False}, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_active"] is False

    def test_customer_cannot_access_admin_users(self, client, db):
        user_id = create_test_user(db, email="cust@example.com", role="customer")
        token = login_user(client, "cust@example.com")
        resp = client.get("/api/admin/users", headers=auth_header(token))
        assert resp.status_code == 403

    def test_seller_cannot_access_admin_users(self, client, db):
        user_id = create_test_user(db, email="selladmin@example.com", role="seller")
        token = login_user(client, "selladmin@example.com")
        resp = client.get("/api/admin/users", headers=auth_header(token))
        assert resp.status_code == 403

    def test_invalid_user_id(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        resp = client.get("/api/admin/users/invalidid", headers=auth_header(token))
        assert resp.status_code == 400

    def test_user_not_found(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        from bson import ObjectId
        fake_id = str(ObjectId())
        resp = client.get(f"/api/admin/users/{fake_id}", headers=auth_header(token))
        assert resp.status_code == 404


# ==================== SELLER PROFILE TESTS ====================

class TestSellerProfile:
    def _setup_seller(self, db, client):
        user_id = create_test_user(db, email="seller@example.com", name="Seller User", role="seller")
        seller_id = create_test_seller(db, user_id, company_name="Seller Corp", is_approved=True)
        token = login_user(client, "seller@example.com")
        return user_id, seller_id, token

    def test_get_seller_profile(self, client, db):
        user_id, seller_id, token = self._setup_seller(db, client)
        resp = client.get("/api/sellers/me", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["company_name"] == "Seller Corp"

    def test_update_seller_profile(self, client, db):
        user_id, seller_id, token = self._setup_seller(db, client)
        resp = client.patch("/api/sellers/me", json={"company_name": "New Corp"}, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["company_name"] == "New Corp"

    def test_customer_cannot_access_seller_profile(self, client, db):
        user_id = create_test_user(db, email="custsprofile@example.com", role="customer")
        token = login_user(client, "custsprofile@example.com")
        resp = client.get("/api/sellers/me", headers=auth_header(token))
        assert resp.status_code == 403

    def test_unapproved_seller_can_access_profile(self, client, db):
        user_id = create_test_user(db, email="unapproved@example.com", role="seller")
        seller_id = create_test_seller(db, user_id, company_name="Unapproved Corp", is_approved=False)
        token = login_user(client, "unapproved@example.com")
        resp = client.get("/api/sellers/me", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["company_name"] == "Unapproved Corp"


# ==================== ADMIN SELLER TESTS ====================

class TestAdminSellers:
    def _setup_admin(self, db, client):
        user_id = create_test_user(db, email="admin_seller@example.com", name="Admin", role="admin")
        token = login_user(client, "admin_seller@example.com")
        return user_id, token

    def test_admin_list_sellers(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        uid1 = create_test_user(db, email="s1@example.com", role="seller")
        create_test_seller(db, uid1, company_name="Seller A")
        uid2 = create_test_user(db, email="s2@example.com", role="seller")
        create_test_seller(db, uid2, company_name="Seller B")
        resp = client.get("/api/admin/sellers", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2

    def test_admin_get_seller(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        uid = create_test_user(db, email="gseller@example.com", role="seller")
        sid = create_test_seller(db, uid, company_name="Get Seller")
        resp = client.get(f"/api/admin/sellers/{sid}", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["company_name"] == "Get Seller"

    def test_admin_approve_seller(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        uid = create_test_user(db, email="approve@example.com", role="seller")
        sid = create_test_seller(db, uid, company_name="Approve Corp", is_approved=False)
        resp = client.patch(f"/api/admin/sellers/{sid}/status",
                           json={"status": "approved"}, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "approved"

    def test_admin_reject_seller(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        uid = create_test_user(db, email="reject@example.com", role="seller")
        sid = create_test_seller(db, uid, company_name="Reject Corp", is_approved=True)
        resp = client.patch(f"/api/admin/sellers/{sid}/status",
                           json={"status": "rejected"}, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"

    def test_admin_suspend_seller(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        uid = create_test_user(db, email="suspend@example.com", role="seller")
        sid = create_test_seller(db, uid, company_name="Suspend Corp", is_approved=True)
        resp = client.patch(f"/api/admin/sellers/{sid}/status",
                           json={"status": "suspended"}, headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"

    def test_customer_cannot_approve_seller(self, client, db):
        uid = create_test_user(db, email="custapprove@example.com", role="customer")
        token = login_user(client, "custapprove@example.com")
        sid = create_test_seller(db, uid, company_name="Cannot Approve")
        resp = client.patch(f"/api/admin/sellers/{sid}/status",
                           json={"status": "approved"}, headers=auth_header(token))
        assert resp.status_code == 403

    def test_seller_cannot_approve_self(self, client, db):
        uid = create_test_user(db, email="selfapprove@example.com", role="seller")
        sid = create_test_seller(db, uid, company_name="Self Approve")
        token = login_user(client, "selfapprove@example.com")
        resp = client.patch(f"/api/admin/sellers/{sid}/status",
                           json={"status": "approved"}, headers=auth_header(token))
        assert resp.status_code == 403

    def test_invalid_seller_id(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        resp = client.get("/api/admin/sellers/invalidid", headers=auth_header(token))
        assert resp.status_code == 400

    def test_seller_not_found(self, client, db):
        admin_id, token = self._setup_admin(db, client)
        from bson import ObjectId
        fake_id = str(ObjectId())
        resp = client.get(f"/api/admin/sellers/{fake_id}", headers=auth_header(token))
        assert resp.status_code == 404


# ==================== SECURITY TESTS ====================

class TestSecurity:
    def test_customer_cannot_access_admin_endpoints(self, client, db):
        uid = create_test_user(db, email="sec_cust@example.com", role="customer")
        token = login_user(client, "sec_cust@example.com")
        assert client.get("/api/admin/users", headers=auth_header(token)).status_code == 403
        assert client.get("/api/admin/sellers", headers=auth_header(token)).status_code == 403

    def test_seller_cannot_access_admin_endpoints(self, client, db):
        uid = create_test_user(db, email="sec_sell@example.com", role="seller")
        token = login_user(client, "sec_sell@example.com")
        assert client.get("/api/admin/users", headers=auth_header(token)).status_code == 403
        assert client.get("/api/admin/sellers", headers=auth_header(token)).status_code == 403

    def test_no_password_hash_in_any_response(self, client, db):
        uid = create_test_user(db, email="no_hash@example.com")
        token = login_user(client, "no_hash@example.com")
        resp = client.get("/api/users/me", headers=auth_header(token))
        assert "password_hash" not in resp.json()

    def test_health_still_works(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["mongodb"] == "connected"
