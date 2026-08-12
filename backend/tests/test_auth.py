import pytest


BASE = "/api/v1/auth"
SIGNUP_URL = f"{BASE}/signup"
LOGIN_URL = f"{BASE}/login"
REFRESH_URL = f"{BASE}/refresh"
ME_URL = f"{BASE}/me"

USER_PAYLOAD = {
    "email": "alice@example.com",
    "password": "SecurePass123!",
    "full_name": "Alice Test",
}


class TestSignup:
    def test_signup_success(self, client):
        resp = client.post(SIGNUP_URL, json=USER_PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == USER_PAYLOAD["email"]
        assert data["full_name"] == USER_PAYLOAD["full_name"]
        assert data["role"] == "USER"
        assert data["is_active"] is True
        assert "hashed_password" not in data

    def test_signup_duplicate_email(self, client):
        resp = client.post(SIGNUP_URL, json=USER_PAYLOAD)
        assert resp.status_code == 409

    def test_signup_short_password(self, client):
        resp = client.post(SIGNUP_URL, json={**USER_PAYLOAD, "email": "b@b.com", "password": "short"})
        assert resp.status_code == 422

    def test_signup_invalid_email(self, client):
        resp = client.post(SIGNUP_URL, json={**USER_PAYLOAD, "email": "not-an-email"})
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        resp = client.post(LOGIN_URL, json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        resp = client.post(LOGIN_URL, json={"email": USER_PAYLOAD["email"], "password": "WrongPass!"})
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post(LOGIN_URL, json={"email": "nobody@example.com", "password": "whatever"})
        assert resp.status_code == 401

    def test_account_lockout_after_5_failures(self, client):
        locked_email = "lockme@example.com"
        # Register the user
        client.post(SIGNUP_URL, json={"email": locked_email, "password": "GoodPass123!", "full_name": "Lock Me"})
        # 5 failed attempts
        for _ in range(5):
            client.post(LOGIN_URL, json={"email": locked_email, "password": "WrongPass!"})
        # 6th attempt should return 423 Locked
        resp = client.post(LOGIN_URL, json={"email": locked_email, "password": "WrongPass!"})
        assert resp.status_code == 423


class TestTokenRefresh:
    def _get_tokens(self, client):
        resp = client.post(LOGIN_URL, json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]})
        return resp.json()

    def test_refresh_success(self, client):
        tokens = self._get_tokens(client)
        resp = client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})
        assert resp.status_code == 200
        new_tokens = resp.json()
        assert "access_token" in new_tokens

    def test_refresh_with_access_token_fails(self, client):
        tokens = self._get_tokens(client)
        resp = client.post(REFRESH_URL, json={"refresh_token": tokens["access_token"]})
        assert resp.status_code == 401

    def test_refresh_with_garbage_token_fails(self, client):
        resp = client.post(REFRESH_URL, json={"refresh_token": "this.is.garbage"})
        assert resp.status_code == 401


class TestMeEndpoint:
    def test_me_returns_user(self, client):
        tokens = client.post(LOGIN_URL, json={"email": USER_PAYLOAD["email"], "password": USER_PAYLOAD["password"]}).json()
        resp = client.get(ME_URL, headers={"Authorization": f"Bearer {tokens['access_token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == USER_PAYLOAD["email"]

    def test_me_without_token(self, client):
        resp = client.get(ME_URL)
        assert resp.status_code in (401, 403)  # HTTPBearer returns 403 in older, 401 in newer Starlette

    def test_me_with_bad_token(self, client):
        resp = client.get(ME_URL, headers={"Authorization": "Bearer bad.token.here"})
        assert resp.status_code == 401
