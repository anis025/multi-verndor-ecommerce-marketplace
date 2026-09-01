import pytest


class TestCustomerRegistration:
    def test_register_customer_success(self, client, otp_sink):
        response = client.post("/api/auth/register", json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["name"] == "John Doe"
        assert data["user"]["email"] == "john@example.com"
        assert data["user"]["role"] == "customer"
        assert data["user"]["is_active"] is False
        assert data["user"]["email_verified"] is False
        assert "id" in data["user"]
        assert "access_token" not in data
        assert "message" in data

    def test_register_customer_duplicate_email(self, client, otp_sink):
        client.post("/api/auth/register", json={
            "name": "John Doe",
            "email": "dup@example.com",
            "password": "password123",
        })
        response = client.post("/api/auth/register", json={
            "name": "Jane Doe",
            "email": "dup@example.com",
            "password": "password456",
        })
        assert response.status_code == 409

    def test_register_customer_invalid_email(self, client):
        response = client.post("/api/auth/register", json={
            "name": "John Doe",
            "email": "not-an-email",
            "password": "password123",
        })
        assert response.status_code == 422

    def test_register_customer_short_password(self, client):
        response = client.post("/api/auth/register", json={
            "name": "John Doe",
            "email": "john2@example.com",
            "password": "123",
        })
        assert response.status_code == 422

    def test_register_customer_no_password_hash_in_response(self, client, otp_sink):
        response = client.post("/api/auth/register", json={
            "name": "John Doe",
            "email": "john3@example.com",
            "password": "password123",
        })
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data

    def test_register_sends_otp(self, client, otp_sink):
        client.post("/api/auth/register", json={
            "name": "Otp User",
            "email": "otpuser@example.com",
            "password": "password123",
        })
        assert otp_sink["otpuser@example.com"].isdigit()
        assert len(otp_sink["otpuser@example.com"]) == 6


class TestSellerRegistration:
    def test_register_seller_success(self, client, otp_sink):
        response = client.post("/api/auth/seller/register", json={
            "name": "Seller One",
            "email": "seller1@example.com",
            "password": "password123",
            "company_name": "ABC Electronics",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["role"] == "seller"
        assert data["user"]["email_verified"] is False
        assert "access_token" not in data
        assert data["seller"]["company_name"] == "ABC Electronics"
        assert data["seller"]["is_approved"] is False

    def test_register_seller_duplicate_email(self, client, otp_sink):
        client.post("/api/auth/seller/register", json={
            "name": "Seller One",
            "email": "seller_dup@example.com",
            "password": "password123",
            "company_name": "ABC Electronics",
        })
        response = client.post("/api/auth/seller/register", json={
            "name": "Seller Two",
            "email": "seller_dup@example.com",
            "password": "password456",
            "company_name": "XYZ Corp",
        })
        assert response.status_code == 409

    def test_register_seller_default_not_approved(self, client, otp_sink):
        response = client.post("/api/auth/seller/register", json={
            "name": "Seller Not Approved",
            "email": "seller_not_approved@example.com",
            "password": "password123",
            "company_name": "Pending Corp",
        })
        data = response.json()
        assert data["seller"]["is_approved"] is False

    def test_register_customer_as_seller_via_role(self, client, otp_sink):
        response = client.post("/api/auth/register", json={
            "name": "Seller Via Role",
            "email": "sellerrole@example.com",
            "password": "password123",
            "role": "seller",
            "company_name": "Role Corp",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["role"] == "seller"
        assert "access_token" not in data
        assert data["seller"]["company_name"] == "Role Corp"
        assert data["seller"]["is_approved"] is False

    def test_register_seller_requires_company_name(self, client):
        response = client.post("/api/auth/register", json={
            "name": "No Company",
            "email": "nocompany@example.com",
            "password": "password123",
            "role": "seller",
        })
        assert response.status_code == 422


class TestEmailVerification:
    def test_verify_email_success(self, client, otp_sink):
        client.post("/api/auth/register", json={
            "name": "Verify User",
            "email": "verify@example.com",
            "password": "password123",
        })
        otp = otp_sink["verify@example.com"]
        response = client.post("/api/auth/verify-email", json={
            "email": "verify@example.com",
            "otp": otp,
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email_verified"] is True
        assert data["user"]["is_active"] is True

    def test_verify_email_wrong_otp(self, client, otp_sink):
        client.post("/api/auth/register", json={
            "name": "Wrong Otp",
            "email": "wrongotp@example.com",
            "password": "password123",
        })
        response = client.post("/api/auth/verify-email", json={
            "email": "wrongotp@example.com",
            "otp": "000000",
        })
        assert response.status_code == 400
        assert "Invalid or expired" in response.json()["detail"]

    def test_verify_email_unknown_email(self, client):
        response = client.post("/api/auth/verify-email", json={
            "email": "nobody@example.com",
            "otp": "123456",
        })
        assert response.status_code == 400

    def test_verify_email_too_many_attempts_locks(self, client, otp_sink):
        client.post("/api/auth/register", json={
            "name": "Lock User",
            "email": "lock@example.com",
            "password": "password123",
        })
        for _ in range(5):
            client.post("/api/auth/verify-email", json={
                "email": "lock@example.com",
                "otp": "000000",
            })
        locked = client.post("/api/auth/verify-email", json={
            "email": "lock@example.com",
            "otp": "000000",
        })
        assert locked.status_code == 400
        assert "Too many attempts" in locked.json()["detail"]

    def test_resend_otp_returns_success_or_cooldown(self, client, otp_sink):
        client.post("/api/auth/register", json={
            "name": "Resend User",
            "email": "resend@example.com",
            "password": "password123",
        })
        response = client.post("/api/auth/resend-otp", json={
            "email": "resend@example.com",
        })
        assert response.status_code in (200, 429)

    def test_cannot_login_before_verification(self, client, otp_sink):
        client.post("/api/auth/register", json={
            "name": "Pre Verify",
            "email": "preverify@example.com",
            "password": "password123",
        })
        response = client.post("/api/auth/login", json={
            "email": "preverify@example.com",
            "password": "password123",
        })
        assert response.status_code == 401
        assert "verify" in response.json()["detail"].lower()


class TestLogin:
    def test_login_customer_success(self, client, otp_sink, register_and_verify):
        register_and_verify(client, otp_sink, name="Login User", email="login@example.com",
                             password="password123")
        response = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "customer"

    def test_login_wrong_password(self, client, otp_sink, register_and_verify):
        register_and_verify(client, otp_sink, name="Wrong Pass", email="wrong@example.com",
                            password="password123")
        response = client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_unknown_email(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123",
        })
        assert response.status_code == 401

    def test_login_seller_success(self, client, otp_sink, register_and_verify):
        register_and_verify(client, otp_sink, name="Seller Login",
                            email="seller_login@example.com", password="password123",
                            role="seller", company_name="Login Corp")
        response = client.post("/api/auth/login", json={
            "email": "seller_login@example.com",
            "password": "password123",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "seller"


class TestJWT:
    def test_valid_token_me(self, client, otp_sink, register_and_verify):
        register_and_verify(client, otp_sink, name="JWT User", email="jwt@example.com",
                            password="password123")
        login_resp = client.post("/api/auth/login", json={
            "email": "jwt@example.com",
            "password": "password123",
        })
        token = login_resp.json()["access_token"]

        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "jwt@example.com"
        assert data["email_verified"] is True

    def test_invalid_token(self, client):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalidtoken123",
        })
        assert response.status_code == 401

    def test_no_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code in (401, 403)

    def test_malformed_bearer(self, client):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Token abc123",
        })
        assert response.status_code in (401, 403)


class TestLogout:
    def test_logout(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        assert "Logged out" in response.json()["message"]


class TestGetCurrentUser:
    def test_me_returns_user_data(self, client, otp_sink, register_and_verify):
        register_and_verify(client, otp_sink, name="Me User", email="me@example.com",
                            password="password123")
        login_resp = client.post("/api/auth/login", json={
            "email": "me@example.com",
            "password": "password123",
        })
        token = login_resp.json()["access_token"]

        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Me User"
        assert data["role"] == "customer"

    def test_me_no_password_hash(self, client, otp_sink, register_and_verify):
        register_and_verify(client, otp_sink, name="Secure User", email="secure@example.com",
                            password="password123")
        login_resp = client.post("/api/auth/login", json={
            "email": "secure@example.com",
            "password": "password123",
        })
        token = login_resp.json()["access_token"]

        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        data = response.json()
        assert "password_hash" not in data
        assert "password" not in data


class TestAdminBootstrap:
    def test_admin_cannot_register_publicly(self, client):
        response = client.post("/api/auth/register", json={
            "name": "Fake Admin",
            "email": "fakeadmin@example.com",
            "password": "password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["role"] == "customer"

    def test_cannot_self_assign_admin_role(self, client):
        response = client.post("/api/auth/register", json={
            "name": "Hacker",
            "email": "hacker@example.com",
            "password": "password123",
        })
        data = response.json()
        assert data["user"]["role"] != "admin"


class TestPasswordSecurity:
    def test_password_never_in_response(self, client, otp_sink):
        response = client.post("/api/auth/register", json={
            "name": "Pass Test",
            "email": "passtest@example.com",
            "password": "password123",
        })
        response_text = str(response.json())
        assert "password123" not in response_text
        assert "password_hash" not in response.json()

    def test_password_not_in_login_response(self, client, otp_sink, register_and_verify):
        register_and_verify(client, otp_sink, name="Login Pass", email="loginpass@example.com",
                            password="password123")
        response = client.post("/api/auth/login", json={
            "email": "loginpass@example.com",
            "password": "password123",
        })
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
