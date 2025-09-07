import pytest
from tests.utils.config import SETTINGS
from pathlib import Path
from uuid import uuid4


@pytest.mark.regression
class TestBlogCRUD:

    @pytest.mark.smoke
    def test_get_list(self, http):
        r = http.get(SETTINGS.blogs_path, params={"page": 1, "page_size": 10})
        assert r.status_code == 200
        j = r.json()
        assert "results" in j or isinstance(j, list)

    @pytest.mark.regression
    def test_create_and_delete_blog(self, http):
        img = Path("tests/resources/banner.jpg")
        assert img.exists()

        base_url = SETTINGS.base_url.rstrip("/")
        blogs_url = f"{base_url}{SETTINGS.blogs_path}"  # ví dụ: /api/v1/blogs/

        # ====== CREATE ======
        title = f"Hello World {uuid4().hex[:6]}"  # tránh trùng
        data = {
            "title": title,
            "category": "5",
            "description": "test api nhe",
            "is_active": "true",
            "tap_chi_van_hoc": "true",
            "tags": ["24", "25"],  # API nhận ID
        }

        with img.open("rb") as f:
            files = {"banner": ("banner.jpg", f, "image/jpeg")}
            resp_create = http.post(blogs_url, data=data, files=files)

        # Kiểm tra tạo thành công
        assert resp_create.status_code in (200, 201), f"Create failed: {resp_create.status_code} - {resp_create.text}"
        assert "application/json" in resp_create.headers.get("Content-Type", "").lower()

        body = resp_create.json()
        blog_id = body.get("id")
        assert blog_id, f"Missing blog_id in response: {body}"

        # Validate dữ liệu trả về
        assert isinstance(body.get("banner"), str) and body["banner"]
        assert body.get("title") == title
        assert str(body.get("category")) in {"5", "{"} or body.get("category")
        assert len(body.get("tags", [])) >= 2

        # ====== DELETE ======
        detail_url = f"{blogs_url}{blog_id}/"  # Ví dụ: /api/v1/blogs/123/
        resp_delete = http.delete(detail_url)

        # Kiểm tra xóa thành công
        assert resp_delete.status_code in (
        200, 202, 204), f"Delete failed: {resp_delete.status_code} - {resp_delete.text}"

        # ====== VERIFY DELETE ======
        resp_get = http.get(detail_url)
        assert resp_get.status_code in (404, 410), f"Expected 404/410 after delete, got {resp_get.status_code}"


    @pytest.mark.regression
    def test_create_blog_without_auth(self, http_public):
        """
        Đảm bảo API tạo blog bị từ chối nếu không có Authorization token.
        """
        img = Path("tests/resources/banner.jpg")
        assert img.exists()

        url = f"{SETTINGS.base_url.rstrip('/')}{SETTINGS.blogs_path}"

        data = {
            "title": "Unauthorized Blog",
            "category": "5",
            "description": "test api without token",
            "is_active": "true",
            "tap_chi_van_hoc": "true",
            "tags": ["24", "25"],
        }

        with img.open("rb") as f:
            files = {"banner": ("banner.jpg", f, "image/jpeg")}
            r = http_public.post(url, data=data, files=files)  # Không có token

        # --- Kiểm tra ---
        # Nếu API bảo vệ đúng, phải trả về 401 hoặc 403
        assert r.status_code in (401, 403), f"Expected 401/403, got {r.status_code} - {r.text}"

        # Đảm bảo body có thông báo lỗi cụ thể
        error_text = r.text.lower()
        assert any(msg in error_text for msg in ["unauthorized", "forbidden", "credentials"]), \
            f"Unexpected error message: {r.text}"

    @pytest.mark.regression
    def test_update_blog(self, http):
        """
        Testcase: Tạo blog mới -> Update blog -> Kiểm tra response
        """
        img = Path("tests/resources/banner.jpg")
        assert img.exists(), f"Test image missing: {img}"
        base_url = SETTINGS.base_url.rstrip("/")
        create_url = f"{base_url}{SETTINGS.blogs_path}"

        create_data = {
            "title": "Blog to update",
            "category": "15",
            "description": "original description",
            "is_active": "true",
            "tap_chi_van_hoc": "true",
            "tags": ["24", "25"],
        }

        with img.open("rb") as f:
            files = {"banner": ("banner.jpg", f, "image/jpeg")}
            resp_create = http.post(create_url, data=create_data, files=files)

        assert resp_create.status_code in (200, 201), f"Create failed: {resp_create.status_code} - {resp_create.text}"
        created_blog = resp_create.json()
        blog_id = created_blog.get("id")
        assert blog_id, "Create response missing blog ID"

        update_url = f"{create_url}{blog_id}/"  # ví dụ: /api/v1/blogs/123/

        update_data = {
            "title": "Blog updated 111",
            "category": "15",
            "description": "updated description 222",
            "is_active": "false",  # cập nhật trạng thái
            "tap_chi_van_hoc": "true",
            "tags": ["25"],  # chỉ còn 1 tag
        }

        with img.open("rb") as f:
            update_files = {"banner": ("banner_updated.jpg", f, "image/jpeg")}
            resp_update = http.put(update_url, data=update_data, files=update_files)

        # ===== Bước 3: Assert response =====
        assert resp_update.status_code in (200, 201), f"Update failed: {resp_update.status_code} - {resp_update.text}"
        updated_blog = resp_update.json()

        # Kiểm tra dữ liệu đã update
        assert updated_blog["id"] == blog_id
        assert updated_blog["title"] == "Blog updated 111"
        assert updated_blog["description"] == "updated description 222"
        assert str(updated_blog["category"]) == "15"
        assert len(updated_blog.get("tags", [])) == 1
        assert isinstance(updated_blog.get("banner"), str) and updated_blog["banner"]

        # ===== Bước 4: GET lại blog để confirm (nếu API hỗ trợ GET) =====
        resp_get = http.get(update_url)
        assert resp_get.status_code == 200
        blog_fetched = resp_get.json()
        assert blog_fetched["title"] == "Blog updated 111"
        assert blog_fetched["description"] == "updated description 222"

        detail_url = f"{create_url}{blog_id}/"  # ví dụ: /api/v1/blogs/123/
        http.delete(detail_url)

    @pytest.mark.regression
    def test_delete_blog(self, http):
        """
        Create -> Delete -> Verify deleted
        """
        img = Path("tests/resources/banner.jpg")
        assert img.exists()

        base = SETTINGS.base_url.rstrip("/")
        create_url = f"{base}{SETTINGS.blogs_path}"

        # --- Create a blog first (để có id) ---
        create_data = {
            "title": "Blog to delete",
            "category": "15",
            "description": "delete me",
            "is_active": "true",
            "tap_chi_van_hoc": "true",
            "tags": ["24", "25"],
        }
        with img.open("rb") as f:
            files = {"banner": ("banner.jpg", f, "image/jpeg")}
            r_create = http.post(create_url, data=create_data, files=files)

        assert r_create.status_code in (200, 201), f"Create failed: {r_create.status_code} - {r_create.text}"
        blog = r_create.json()
        blog_id = blog.get("id")
        assert blog_id, "Create response missing blog ID"

        # --- Delete ---
        detail_url = f"{create_url}{blog_id}/"  # ví dụ: /api/v1/blogs/123/
        r_del = http.delete(detail_url)
        assert r_del.status_code in (200, 202, 204), f"Delete failed: {r_del.status_code} - {r_del.text}"

        # --- Verify deleted (tuỳ API) ---
        r_get = http.get(detail_url)
        assert r_get.status_code in (404, 410), f"Expected 404/410 after delete, got {r_get.status_code} - {r_get.text}"

    @pytest.mark.regression
    def test_delete_blog_without_auth(self, http_public):
        """
        Ensure delete requires auth
        """
        # Dùng id tuỳ môi trường; nếu không chắc tồn tại, có thể tạo trước rồi gọi http_public.delete
        blog_id = 63
        url = f"{SETTINGS.base_url.rstrip('/')}{SETTINGS.blogs_path}{blog_id}/"

        r = http_public.delete(url)
        assert r.status_code in (401, 403), f"Expected 401/403, got {r.status_code} - {r.text}"