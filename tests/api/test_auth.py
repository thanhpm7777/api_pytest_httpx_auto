import pytest
from tests.utils.config import SETTINGS
from uuid import uuid4

@pytest.mark.smoke
def test_login_success(http_public):
    r = http_public.post(SETTINGS.login_path, json={
    "username": SETTINGS.username,
    "password": SETTINGS.password
    })
    assert r.status_code in (200, 201)
    j = r.json()
    assert any(k in j for k in ("access", "token", "access_token"))


@pytest.mark.regression
def test_register_then_login(http_public):
    # Sinh username và email ngẫu nhiên
    unique_id = uuid4().hex[:6]  # 6 ký tự đủ ngắn gọn
    username = f"e2e_user_{unique_id}"
    email = f"{username}@example.com"

    new_user = {
        "username": username,
        "email": email,
        "password": "VeryStrong!123",
        "confirm_password": "VeryStrong!123"
    }

    r = http_public.post(SETTINGS.register_path, json=new_user)
    assert r.status_code in (200, 201), f"Register failed: {r.status_code} - {r.text}"

    body = r.json()
    assert body.get("username") == new_user["username"], f"Expected {username}, got {body.get('username')}"
    assert body.get("email") == new_user["email"], f"Expected {email}, got {body.get('email')}"

    login_payload = {
        "username": username,
        "password": new_user["password"],
    }
    login_resp = http_public.post(SETTINGS.login_path, json=login_payload)
    assert login_resp.status_code in (200, 201), f"Login failed: {login_resp.status_code} - {login_resp.text}"

    login_data = login_resp.json()
    assert any(k in login_data for k in ("access", "token", "access_token")), \
        f"Token missing in response: {login_data}"

