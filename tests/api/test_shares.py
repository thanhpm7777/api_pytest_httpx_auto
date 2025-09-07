# import pytest
# from tests.utils.config import SETTINGS
#
#
# def test_share_create(http):
#     r = http.post(SETTINGS.blogs_path, json={"title": "Share me", "content": "..."})
#     blog_id = r.json()["id"]
#
#
#     s = http.post(SETTINGS.shares_path, json={"blog": blog_id, "channel": "facebook"})
#     assert s.status_code in (200, 201)