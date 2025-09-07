from typing import Optional
from .config import SETTINGS
from .http_client import client


_TOKEN_CACHE: Optional[str] = None


def login_and_get_token(username: str | None = None, password: str | None = None) -> str:
    global _TOKEN_CACHE
    if _TOKEN_CACHE:
        return _TOKEN_CACHE
    username = username or SETTINGS.username
    password = password or SETTINGS.password
    assert username and password, "USERNAME/PASSWORD must be set in environment/.env"

    with client() as c:
        resp = c.post(SETTINGS.login_path, json={"username": username, "password": password})
    assert resp.status_code in (200, 201), f"Login failed: {resp.status_code} {resp.text}"
    data = resp.json()
    token = data.get("access") or data.get("token") or data.get("access_token")
    assert token, f"Token key not found in response: {data}"
    _TOKEN_CACHE = token
    return token