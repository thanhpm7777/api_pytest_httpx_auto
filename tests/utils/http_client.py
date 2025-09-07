import httpx
from contextlib import contextmanager
from .config import SETTINGS


DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=10.0)


@contextmanager
def client(token: str | None = None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with httpx.Client(base_url=SETTINGS.base_url, headers=headers, timeout=DEFAULT_TIMEOUT) as c:
        yield c