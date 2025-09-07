import pytest
from pathlib import Path
from uuid import uuid4
from tests.utils.config import SETTINGS

def _create_blog(http) -> int:
    """Tạo blog tối thiểu, trả về blog_id."""
    img = Path("tests/resources/banner.jpg")
    assert img.exists(), "Missing test image: tests/resources/banner.jpg"

    base = SETTINGS.base_url.rstrip("/")
    blogs_url = f"{base}{SETTINGS.blogs_path}"  # ví dụ: /api/v1/blog/ hoặc /api/v1/blogs/
    data = {
        "title": f"Like target {uuid4().hex[:6]}",
        "category": "5",
        "description": "blog for like/unlike tests",
        "is_active": "true",
        "tap_chi_van_hoc": "true",
        "tags": ["24", "25"],
    }
    with img.open("rb") as f:
        files = {"banner": ("banner.jpg", f, "image/jpeg")}
        r = http.post(blogs_url, data=data, files=files)
    assert r.status_code in (200, 201), f"Create failed: {r.status_code} - {r.text}"
    blog_id = r.json().get("id")
    assert blog_id, f"Missing blog id: {r.text}"
    return blog_id


@pytest.mark.regression
def test_like_then_unlike_blog( http):
    """Happy path: Like rồi Unlike cùng 1 blog (có token)."""
    base = SETTINGS.base_url.rstrip("/")
    blogs_base = f"{base}{SETTINGS.blogs_path}"     # e.g. /api/v1/blog/
    blog_id = _create_blog(http)
    detail = f"{blogs_base}{blog_id}/"
    like_url = f"{detail}like/"

    # --- LIKE ---
    r_like = http.post(like_url)
    assert r_like.status_code in (200, 201), f"Like failed: {r_like.status_code} - {r_like.text}"
    like_body = {}
    try:
        like_body = r_like.json()
    except Exception:
        pass
    # Nếu API có 'liked' hoặc 'likes_count' thì kiểm tra nhẹ
    if isinstance(like_body, dict):
        if "liked" in like_body:
            assert like_body["liked"] is True
        if "likes_count" in like_body:
            assert isinstance(like_body["likes_count"], int) and like_body["likes_count"] >= 1

    # --- UNLIKE ---
    # Ưu tiên DELETE /like/, nếu 405 -> thử POST /unlike/
    r_unlike = http.delete(like_url)
    if r_unlike.status_code == 405:
        unlike_url = f"{detail}unlike/"
        r_unlike = http.post(unlike_url)

    assert r_unlike.status_code in (200, 202, 204), f"Unlike failed: {r_unlike.status_code} - {r_unlike.text}"

    # (Tuỳ API) GET lại blog để confirm trạng thái
    r_get = http.get(detail)
    if r_get.status_code == 200:
        body = r_get.json()
        # Nếu server có flag/đếm like
        if isinstance(body, dict):
            if "liked" in body:
                assert body["liked"] in (False, None)
            if "likes_count" in body:
                assert isinstance(body["likes_count"], int) and body["likes_count"] >= 0

    # Cleanup
    http.delete(detail)


@pytest.mark.regression
def test_like_requires_auth( http, http_public):
    """Negative: Không token mà gọi like thì phải bị 401/403."""
    base = SETTINGS.base_url.rstrip("/")
    blogs_base = f"{base}{SETTINGS.blogs_path}"
    blog_id = _create_blog(http)              # tạo bằng client có token
    detail = f"{blogs_base}{blog_id}/"
    like_url = f"{detail}like/"

    r = http_public.post(like_url)            # gọi like bằng client KHÔNG token
    assert r.status_code in (401, 403), f"Expected 401/403, got {r.status_code} - {r.text}"

    # Cleanup
    http.delete(detail)
