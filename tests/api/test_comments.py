import pytest
from pathlib import Path
from uuid import uuid4
from tests.utils.config import SETTINGS

@pytest.mark.regression
def test_add_and_list_comment( http):
    """
    Testcase: Tạo blog -> Thêm comment -> Lấy danh sách comment
    """
    img = Path("tests/resources/banner.jpg")
    assert img.exists(), "Test image missing!"

    base_url = SETTINGS.base_url.rstrip("/")
    blogs_url = f"{base_url}{SETTINGS.blogs_path}"   # /api/v1/blog/

    # ==== Step 1: Tạo blog trước ====
    unique_title = f"Blog for comment {uuid4().hex[:6]}"
    blog_payload = {
        "title": unique_title,
        "category": "5",
        "description": "This blog is created for comment testing",
        "is_active": "true",
        "tap_chi_van_hoc": "true",
        "tags": ["24", "25"],
    }

    with img.open("rb") as f:
        files = {"banner": ("banner.jpg", f, "image/jpeg")}
        resp_blog = http.post(blogs_url, data=blog_payload, files=files)

    assert resp_blog.status_code in (200, 201), f"Create blog failed: {resp_blog.status_code} - {resp_blog.text}"
    blog_id = resp_blog.json().get("id")
    assert blog_id, f"Missing blog id in response: {resp_blog.json()}"

    # ==== Step 2: Thêm comment vào blog ====
    comments_url = f"{blogs_url}{blog_id}/comments/"  # /api/v1/blog/50/comments/
    comment_text = f"Comment content {uuid4().hex[:4]}"

    resp_comment = http.post(comments_url, json={"text": comment_text})
    assert resp_comment.status_code in (200, 201), f"Add comment failed: {resp_comment.status_code} - {resp_comment.text}"

    comment_body = resp_comment.json()
    assert comment_body.get("id"), f"Comment response missing id: {comment_body}"
    assert comment_body.get("text") == comment_text

    # ==== Step 3: Lấy danh sách comment của blog ====
    resp_list = http.get(comments_url)
    assert resp_list.status_code == 200, f"List comments failed: {resp_list.status_code} - {resp_list.text}"

    data = resp_list.json()
    # Hỗ trợ cả dạng paginated hoặc list đơn
    if isinstance(data, dict) and "results" in data:
        comments = data["results"]
    elif isinstance(data, list):
        comments = data
    else:
        raise AssertionError(f"Unexpected response format: {data}")

    # Xác minh comment vừa thêm nằm trong danh sách
    assert any(c["id"] == comment_body["id"] for c in comments), "New comment not found in list"

    # ==== Step 4: Cleanup - Xóa blog để dữ liệu sạch ====
    delete_url = f"{blogs_url}{blog_id}/"
    http.delete(delete_url)
